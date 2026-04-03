import numpy as np
from .quaternion import Point3D, KADMON_3D_POINTS, mandelbulb_stability

class MacroTriangulation:
    """
    3D User-Query-AI triangulation engine
    Physics engine for human-AI alignment
    """
    
    def __init__(self):
        self.absolute_center = KADMON_3D_POINTS["absolute_center"]
        self.user_point = KADMON_3D_POINTS["user_anchor"]
        self.query_point = None
        self.ai_resolved_point = None
        
    def execute_second_order(self, mode: str = "COUPLE", agent1_z: float = 0.0, agent2_z: float = 0.0):
        """
        Resolve AI position in 3D space based on 2nd order mode
        
        PAIR: Unified oracle - both agents share absolute center
        COUPLE: Projective engine - agents split and project new center
        """
        if mode == "PAIR":
            self.ai_resolved_point = self.absolute_center
            
        elif mode == "COUPLE":
            p1 = Point3D(-0.75, 0.125, agent1_z)
            p2 = Point3D(-0.75, -0.125, agent2_z)
            
            # Project synthetic center point between agents using Mandelbulb math
            midpoint = (p1 + p2) * 0.5
            
            # Find stable point along normal vector between agents
            stability = mandelbulb_stability(midpoint)
            
            # Adjust z position based on stability
            self.ai_resolved_point = Point3D(
                midpoint.x,
                midpoint.y,
                midpoint.z * stability
            )
    
    def set_query_position(self, x: float, y: float, z: float):
        """Set query position in 3D cognitive space"""
        self.query_point = Point3D(x, y, z)
    
    def calculate_alignment(self):
        """
        Calculate macro triangle properties:
        User ↔ Query ↔ AI
        
        Returns alignment metrics that define the final response trajectory
        """
        if not all([self.user_point, self.query_point, self.ai_resolved_point]):
            raise ValueError("All three points required for triangulation")
        
        # Create edge vectors
        uq = self.query_point.coords - self.user_point.coords
        ua = self.ai_resolved_point.coords - self.user_point.coords
        qa = self.ai_resolved_point.coords - self.query_point.coords
        
        # Plane normal vector = 4D direction of answer
        normal_vector = np.cross(uq, ua)
        
        # Triangle area = cognitive distance / alignment gap
        alignment_gap_area = np.linalg.norm(normal_vector) / 2.0
        
        # Side lengths
        side_lengths = {
            "user_to_query": np.linalg.norm(uq),
            "query_to_ai": np.linalg.norm(qa),
            "user_to_ai": np.linalg.norm(ua)
        }
        
        # Alignment threshold
        ALIGNMENT_THRESHOLD = 0.1
        is_aligned = alignment_gap_area < ALIGNMENT_THRESHOLD
        
        return {
            "user_point": str(self.user_point),
            "query_point": str(self.query_point),
            "ai_resolved_point": str(self.ai_resolved_point),
            "plane_normal": normal_vector.tolist(),
            "alignment_gap_area": alignment_gap_area,
            "side_lengths": side_lengths,
            "is_aligned": is_aligned,
            "mandelbulb_stability": mandelbulb_stability(self.ai_resolved_point)
        }
    
    def get_optimal_ai_target(self):
        """Calculate perfect alignment target point"""
        # Optimal point is plane centroid when perfectly aligned
        return (self.user_point + self.query_point + self.absolute_center) * (1/3)
