import cmath
import uuid
from datetime import datetime

# Canonical coordinates from mbrot11.png
KADMON_POINTS = {
    "container": complex(-0.75, 0.0),
    "stability_anchor": complex(-0.500003, 0.0),
    "triangle_upper": complex(-0.75, 0.125),
    "triangle_lower": complex(-0.75, -0.125),
    "bulb_upper_center": complex(-0.875, 0.2165),
    "bulb_lower_center": complex(-0.875, -0.2165),
    "cardioid_root": complex(-0.75, 0.0)
}

VALID_NODES = list(KADMON_POINTS.values())

def mandelbrot_stability(c: complex, max_iter: int = 200) -> float:
    """Calculate mathematical stability of a point in Mandelbrot set"""
    z = 0j
    for i in range(max_iter):
        z = z * z + c
        if abs(z) > 2:
            return i / max_iter
    return 1.0

class KadmonNegotiation:
    def __init__(self):
        self.round = 0
        self.problem_position = KADMON_POINTS["container"]
        self.agent1_position = KADMON_POINTS["triangle_upper"]
        self.agent2_position = KADMON_POINTS["triangle_lower"]
        self.history = []
        self.complete = False
        self.agreed_position = None
        
    def allowed_moves(self, current_position: complex):
        """Return all valid nodes an agent may move to"""
        return [p for p in VALID_NODES if p != current_position]
        
    def agent_move(self, agent_id: str, new_position: complex):
        """Record an agent move"""
        if new_position not in VALID_NODES:
            raise ValueError(f"Invalid position: {new_position}")
            
        if agent_id == "agent_1":
            self.agent1_position = new_position
        elif agent_id == "agent_2":
            self.agent2_position = new_position
            
        self._log_move(agent_id, "move_self", new_position)
        
    def propose_problem_move(self, agent_id: str, new_position: complex):
        """Propose moving the problem container"""
        if new_position not in VALID_NODES:
            raise ValueError(f"Invalid position: {new_position}")
            
        self.problem_position = new_position
        self._log_move(agent_id, "move_problem", new_position)
        
    def calculate_stability(self):
        """Calculate dual stability metric"""
        math_stability = mandelbrot_stability(self.problem_position)
        return {
            "mathematical": math_stability,
            "problem_position": str(self.problem_position),
            "agent1_position": str(self.agent1_position),
            "agent2_position": str(self.agent2_position),
            "round": self.round
        }
        
    def check_consensus(self, semantic_stability: float):
        """Check if consensus conditions are met"""
        math_stability = mandelbrot_stability(self.problem_position)
        
        if math_stability > 0.75 and semantic_stability > 0.85:
            self.complete = True
            self.agreed_position = self.problem_position
            return True
        return False
        
    def _log_move(self, agent_id, move_type, position):
        self.round += 1
        self.history.append({
            "trace_id": f"TRJ_{str(uuid.uuid4())}",
            "round": self.round,
            "agent_id": agent_id,
            "move_type": move_type,
            "position": str(position),
            "problem_position": str(self.problem_position),
            "timestamp": datetime.utcnow().isoformat().replace('+00:00', 'Z'),
            "stability": self.calculate_stability()
        })
