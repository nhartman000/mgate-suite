import uuid
from collections import deque
from .model_adapter import call_model
from .kadmon import KadmonNegotiation
from .nych import NYCHBridge

class Executor:
    def __init__(self, project, audit):
        self.nych_bridge = NYCHBridge()
        self.project = project
        self.gitson = project.gitson
        self.gst = project.gst
        self.audit = audit
        self.gates = {g["gate_id"]: g for g in self.gitson["gates"]}
        self.node_traces = {}

    def topological_sort(self):
        nodes = self.gitson['graph']['nodes']
        edges = self.gitson['graph']['edges']
        
        in_degree = {node: 0 for node in nodes}
        adj = {node: [] for node in nodes}
        
        for edge in edges:
            adj[edge['from']].append(edge['to'])
            in_degree[edge['to']] += 1
        
        queue = deque([node for node in nodes if in_degree[node] == 0])
        topo_order = []
        
        while queue:
            node = queue.popleft()
            topo_order.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(topo_order) != len(nodes):
            raise ValueError("DAG contains cycle")
        return topo_order

    def get_parent_trace_ids(self, gate_id):
        edges = self.gitson['graph']['edges']
        parents = [e['from'] for e in edges if e['to'] == gate_id]
        
        if not parents:
            return [self.audit.run_trace_id], self.audit.run_trace_id
        
        parent_traces = [self.node_traces[p] for p in parents if p in self.node_traces]
        if not parent_traces:
            return [self.audit.run_trace_id], self.audit.run_trace_id
            
        return parent_traces, parent_traces[-1]

    def run(self):
        # Check if this is a Kadmon negotiation gate
        if any(g.get('gate_type') == 'KADMON' for g in self.gates.values()):
            return self._run_kadmon_negotiation()
            
        execution_order = []
        visited = set()
        
        if not self.gitson['graph']['nodes']:
            raise ValueError("No nodes defined in graph")
            
        current_gate = self.gitson['graph']['nodes'][0]
        
        while current_gate and current_gate not in visited:
            visited.add(current_gate)
            execution_order.append(current_gate)
            
            gate = self.gates[current_gate]
            
            trace_id = f"TRJ_{str(uuid.uuid4())}"
            self.node_traces[current_gate] = trace_id
            
            parent_trace_ids, parent_trace_id = self.get_parent_trace_ids(current_gate)
            
            # Evaluate boolean gate conditions
            condition_results = []
            if 'conditions' in gate:
                for cond in gate['conditions']:
                    left = cond['left']
                    op = cond['operator']
                    right = cond['right']
                    
                    if op == '=':
                        res = (left == right)
                    elif op == '!=':
                        res = (left != right)
                    elif op == '>':
                        res = (left > right)
                    elif op == '<':
                        res = (left < right)
                    elif op == '>=':
                        res = (left >= right)
                    elif op == '<=':
                        res = (left <= right)
                    elif op == 'contains':
                        res = (str(right) in str(left))
                    else:
                        res = False
                    
                    condition_results.append(res)
            
            # Evaluate base logic for boolean gates early
            gate_type = gate.get('gate_type', 'BOOLEAN')
            if gate_type == 'AND':
                gate_passed = all(condition_results)
            elif gate_type == 'OR':
                gate_passed = any(condition_results)
            elif gate_type == 'NAND':
                gate_passed = not all(condition_results)
            elif gate_type == 'NOR':
                gate_passed = not any(condition_results)
            elif gate_type == 'BOOLEAN':
                gate_passed = condition_results[0] if condition_results else True
            elif gate_type in ['tote_test', 'tote_operate', 'transform', 'condition']:
                gate_passed = None # Placeholder, logic evaluates after prompt response
            else:
                gate_passed = False
            
            base_prompt = gate['prompt_template']
            if 'adsr' in gate:
                adsr = gate['adsr']
                base_prompt += f"\n[ADSR Params: A={adsr.get('attack',1.0)}, D={adsr.get('decay',0.8)}, S={adsr.get('sustain',1.0)}, R={adsr.get('release',0.7)}, Pan={adsr.get('pan',0.0)}]"
            if 'modality' in gate:
                base_prompt += f"\n[Modality Applied: {gate['modality']}]"

            prompt = f"{self.gst['interpretation_posture']}: {base_prompt}"
            prompt = self.nych_bridge.inject_prompt_header(prompt)
            
            model_name = self.project.mg8.get('model', 'gemini-3-flash-preview')
            model_output = call_model(prompt, model_name, self.project.mg8.get('seed'))
            
            if gate_type in ['tote_test', 'tote_operate', 'transform', 'condition']:
                if gate_type == 'tote_test':
                    # Looking for deterministic success tokens in response
                    gate_passed = any(term in str(model_output).lower() for term in ["success", "done", "nailed_down", "match", "yes", "true"])
                else:
                    # Operate and Transform gates generally run actions but are considered 'passed' sequentially
                    gate_passed = True
            
            confidence = 0.9 if gate_passed else 0.2
            ambiguity = False
            decision = "approve" if gate_passed else "reject"
            status = "pass" if gate_passed else "fail"
            rule_triggered = [r['req_id'] for r in gate.get('atomic_requirements', [])]
            
            event = {
                "trace_id": trace_id,
                "parent_trace_id": parent_trace_id,
                "parent_trace_ids": parent_trace_ids if len(parent_trace_ids) > 1 else None,
                "run_trace_id": self.audit.run_trace_id,
                "source_objects": {"gate_id": current_gate, "gst_id": self.gst['context_id']},
                "source_paths": {
                    "mg8": self.project.mg8_rel_path,
                    "gitson": self.project.gitson_rel_path,
                    "gst": self.project.gst_rel_path
                },
                "decision": decision,
                "status": status,
                "confidence_at_decision": confidence,
                "ambiguity": ambiguity,
                "rule_triggered": rule_triggered
            }
            
            self.audit.log_event(event)
            
            # Conditional routing
            if 'routing' in gate:
                if gate_passed and 'on_true' in gate['routing']:
                    current_gate = gate['routing']['on_true']
                elif not gate_passed and 'on_false' in gate['routing']:
                    current_gate = gate['routing']['on_false']
                else:
                    current_gate = None
            else:
                current_gate = None
        
        return self.audit.data
        
    def _run_kadmon_negotiation(self):
        kadmon = KadmonNegotiation()
        max_rounds = 20
        
        for round in range(max_rounds):
            # Agent 1 turn
            stability = kadmon.calculate_stability()
            
            event = {
                "trace_id": f"TRJ_{str(uuid.uuid4())}",
                "parent_trace_id": self.audit.run_trace_id,
                "run_trace_id": self.audit.run_trace_id,
                "source_objects": {"gate_id": "KADMON", "round": round},
                "source_paths": {
                    "mg8": self.project.mg8_rel_path,
                    "gitson": self.project.gitson_rel_path,
                    "gst": self.project.gst_rel_path
                },
                "kadmon": stability,
                "decision": "propose",
                "status": "negotiating",
                "confidence_at_decision": stability['mathematical'],
                "ambiguity": False,
                "rule_triggered": []
            }
            
            self.audit.log_event(event)
            
            # Check for consensus
            if kadmon.check_consensus(0.9):
                final_event = event.copy()
                final_event["status"] = "consensus"
                final_event["decision"] = "accept"
                self.audit.log_event(final_event)
                break
                
        return self.audit.data
