import uuid
from datetime import datetime
from .kadmon import KADMON_POINTS, KadmonNegotiation, mandelbrot_stability
from .model_adapter import call_model
from .loader import load_project
from .audit import AuditLog

KADMON_SCHEMA_HEADER = """
KADMON SCHEMA HEADER:
1st Ordered Dimension: Time axis
2nd Ordered Dimension: Y axis
3rd Ordered Dimension: Z axis (volumetric)
4th Ordered Dimension: INVARIANT CENTER = C = -0.500003

This is your frame of reference.
All positions are relative to this center point.
This center point is fixed and invariant.
All operations occur within the Kadmon runtime environment.
"""

class KadmonEnvironment:
    """1st Order System: Kadmon Runtime Environment"""
    
    def __init__(self):
        self.center_point = KADMON_POINTS["stability_anchor"]
        self.environment_id = f"KADMON_{str(uuid.uuid4())}"
        self.start_time = datetime.utcnow()
        self.running = False
        self.contained_systems = {
            "second_order": [],
            "third_order": [],
            "fourth_order": []
        }
        
    def start(self):
        """Initialize 1st order environment"""
        self.running = True
        self.run_trace_id = f"RUN_{str(uuid.uuid4())}"
        
    def register_llm(self, model_name, agent_id):
        """Register 3rd order LLM system"""
        if not self.running:
            raise Exception("Kadmon environment not started")
            
        llm = {
            "agent_id": agent_id,
            "model_name": model_name,
            "center_point": self.center_point,
            "registered": datetime.utcnow()
        }
        
        self.contained_systems["third_order"].append(llm)
        return llm
        
    def create_pair(self, agent1_model, agent2_model, mode="PAIR"):
        """Create 2nd order PAIR/COUPLE system"""
        if not self.running:
            raise Exception("Kadmon environment not started")
            
        agent1 = self.register_llm(agent1_model, "agent_1")
        agent2 = self.register_llm(agent2_model, "agent_2")
        
        pair = {
            "mode": mode,
            "agent1": agent1,
            "agent2": agent2,
            "shared_center": self.center_point,
            "iu_position": KADMON_POINTS["container"]
        }
        
        self.contained_systems["second_order"].append(pair)
        return pair
        
    def call_llm(self, agent_id, prompt, seed=None):
        """Schema enforced LLM call. 3rd order systems have no agency."""
        full_prompt = KADMON_SCHEMA_HEADER + "\n" + prompt
        response = call_model(full_prompt, seed)
        return response
        
    def execute_mgate(self, mg8_path):
        """Execute 4th order MGATE system within environment"""
        if not self.running:
            raise Exception("Kadmon environment not started")
            
        project = load_project(mg8_path)
        audit = AuditLog(project.gst['context_id'], project.mg8['model'])
        
        from .executor import Executor
        executor = Executor(project, audit)
        result = executor.run()
        
        self.contained_systems["fourth_order"].append({
            "mg8_path": mg8_path,
            "run_trace_id": audit.run_trace_id
        })
        
        return result
        
    def run_negotiation(self, pair, max_rounds=20):
        """Run 2nd order PAIR negotiation"""
        kadmon = KadmonNegotiation()
        
        for round in range(max_rounds):
            # Agent 1 turn
            response1 = self.call_llm(pair['agent1']['agent_id'], 
                                     f"Round {round}. Current position: {kadmon.problem_position}")
            
            # Agent 2 turn
            response2 = self.call_llm(pair['agent2']['agent_id'], 
                                     f"Round {round}. Evaluate position: {kadmon.problem_position}")
            
            stability = kadmon.calculate_stability()
            
            if kadmon.check_consensus(0.85):
                return {
                    "consensus": True,
                    "agreed_position": kadmon.agreed_position,
                    "rounds": round,
                    "stability": stability,
                    "history": kadmon.history
                }
                
        return {
            "consensus": False,
            "rounds": max_rounds,
            "history": kadmon.history
        }
        
    def shutdown(self):
        self.running = False
