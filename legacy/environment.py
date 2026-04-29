import uuid
from datetime import datetime
from typing import Any
from .kadmon import KADMON_POINTS, KadmonNegotiation, mandelbrot_stability
from .model_adapter import call_model
from .loader import load_project
from .audit import AuditLog
from .mcp_memory import MemoryServerBridge
from .nych import NYCHBridge
from .plugin_registry import KadmonPluginRegistry, PluginManifest, PluginOrder

KADMON_SCHEMA_HEADER = """
KADMON SCHEMA HEADER:
1st Ordered Dimension: Time — high preference for X axis
2nd Ordered Dimension: Stance — high preference for Y axis
3rd Ordered Dimension: Abstraction (volumetric) — high preference for Z axis
4th Ordered Dimension: INVARIANT CENTER = C = -0.500003 (context, frame of reference)

You are operating within the Kadmon Runtime Environment.
Your center point is fixed at C = -0.500003.
All positions are relative to this invariant center point.
You have no agency. Kadmon initiates all calls.
This schema is enforced on every prompt.
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
            "fourth_order": [],
            "fifth_order": []
        }
        self.memory_bridge = MemoryServerBridge(self)
        self.nych_bridge = NYCHBridge()
        # Plugin registry — modular system attachment point
        self.plugin_registry = KadmonPluginRegistry(self)
        
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
            prompt1 = f"Round {round}. Current position: {kadmon.problem_position}"
            response1 = self.call_llm("agent_1", prompt1)
            
            # Agent 2 turn
            prompt2 = f"Round {round}. Evaluate position: {kadmon.problem_position}"
            response2 = self.call_llm("agent_2", prompt2)
            
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
        
    def create_memory_server(self, context_id: str = None) -> str:
        """Create 4th order MCP Memory Server instance accessible from 1st order"""
        return self.memory_bridge.create_memory_server(context_id)
    
    def memory_write(self, context_id: str, key: str, value: Any) -> str:
        """Write to 4th order memory server from 1st order environment"""
        return self.memory_bridge.memory_write(context_id, key, value)
    
    def memory_read(self, context_id: str, key: str) -> Any:
        """Read from 4th order memory server from 1st order environment"""
        return self.memory_bridge.memory_read(context_id, key)
    
    def memory_scan(self, context_id: str, prefix: str) -> list:
        """Scan 4th order memory server from 1st order environment"""
        return self.memory_bridge.memory_scan(context_id, prefix)
    
    def get_memory_server(self, context_id: str):
        """Get direct reference to 4th order memory server (for internal use)"""
        return self.memory_bridge.get_server(context_id)
    
    def enable_nych(self):
        """Enable 5th order NYCH system at current environment level"""
        self.nych_bridge.attach(self, 1)
        self.contained_systems["fifth_order"].append({
            "type": "nych_encoder",
            "attached_at": datetime.utcnow(),
            "order_level": 5
        })
    
    def nych_process(self, text: str) -> dict:
        """Process natural language through 5th order NYCH system"""
        if not self.nych_bridge.attached_to:
            self.enable_nych()
        return self.nych_bridge.process_input(text)
    
    def shutdown(self):
        self.running = False

    def register_plugin(self, manifest: PluginManifest):
        """Register a custom plugin manifest with the environment."""
        self.plugin_registry.register_manifest(manifest)

    def install_plugin(self, plugin_id: str, config: dict = None):
        """Install a plugin by id. Returns the PluginInstance."""
        if not self.running:
            raise Exception("Kadmon environment not started")
        instance = self.plugin_registry.install(plugin_id, config)
        return instance

    def enable_plugin(self, instance_id: str):
        """Enable an installed plugin. Activates its runtime object."""
        return self.plugin_registry.enable(instance_id)

    def disable_plugin(self, instance_id: str):
        """Disable a running plugin."""
        return self.plugin_registry.disable(instance_id)

    def uninstall_plugin(self, instance_id: str):
        """Uninstall a disabled plugin."""
        self.plugin_registry.uninstall(instance_id)

    def get_plugins(self, order=None):
        """Return all plugin instances, optionally filtered by order level."""
        return self.plugin_registry.get_instances(order)

    def list_available_plugins(self):
        """Return all available plugin manifests."""
        return self.plugin_registry.list_available()

    def plugin_status(self):
        """Return full plugin registry snapshot as dict."""
        return self.plugin_registry.to_dict()

    def on_plugin_event(self, event: str, callback):
        """Subscribe to plugin lifecycle events."""
        self.plugin_registry.subscribe(event, callback)

    def call_llm(self, agent_id, prompt, seed=None):
        # REPLACE existing call_llm — now also emits a plugin event for observability
        agent_markers = {
            "agent_1": "AGENT: 1",
            "agent_2": "AGENT: 2",
        }
        # Support dynamic agent IDs like agent_3, agent_4, etc.
        if agent_id.startswith("agent_"):
            try:
                n = int(agent_id.split("_")[1])
                agent_header = f"AGENT: {n}"
            except (IndexError, ValueError):
                agent_header = agent_markers.get(agent_id, "")
        else:
            agent_header = ""

        full_prompt = (agent_header + "\n" if agent_header else "") + KADMON_SCHEMA_HEADER + "\n" + prompt
        response = call_model(full_prompt, seed)

        # Emit event for any plugin event subscribers
        self.plugin_registry.emit("llm_call", {
            "agent_id": agent_id,
            "prompt_length": len(full_prompt),
            "response_length": len(str(response))
        })

        return response
