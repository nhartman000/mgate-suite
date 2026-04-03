import numpy as np

class Point3D:
    """3D coordinate in Kadmon cognitive geometry"""
    def __init__(self, x: float, y: float, z: float):
        self.coords = np.array([x, y, z], dtype=np.float64)
    
    @property
    def x(self): return self.coords[0]
    @property
    def y(self): return self.coords[1]
    @property
    def z(self): return self.coords[2]
    
    def distance_to(self, other: 'Point3D') -> float:
        return np.linalg.norm(self.coords - other.coords)
    
    def __add__(self, other):
        return Point3D(*(self.coords + other.coords))
    
    def __mul__(self, scalar):
        return Point3D(*(self.coords * scalar))
    
    def __repr__(self):
        return f"Point3D({self.x:.6f}, {self.y:.6f}, {self.z:.6f})"


class Quaternion:
    """4D absolute reference frame: w + xi + yj + zk
    w = 4th dimension = invariant model center
    x,y,z = 3D cognitive space
    """
    def __init__(self, w: float, x: float, y: float, z: float):
        self.values = np.array([w, x, y, z], dtype=np.float64)
    
    @property
    def w(self): return self.values[0]
    @property
    def x(self): return self.values[1]
    @property
    def y(self): return self.values[2]
    @property
    def z(self): return self.values[3]
    
    def to_point3d(self) -> Point3D:
        """Project 4D quaternion into 3D cognitive space"""
        return Point3D(self.x, self.y, self.z)


# Canonical 3D coordinates
KADMON_3D_POINTS = {
    "absolute_center": Point3D(-0.500003, 0.0, 0.0),  # 4D w anchor
    "container": Point3D(-0.75, 0.0, 0.0),
    "triangle_upper": Point3D(-0.75, 0.125, 0.0),
    "triangle_lower": Point3D(-0.75, -0.125, 0.0),
    "user_anchor": Point3D(-1.31, 0.0, 0.0),  # Period 4 bulb. Human position.
    "bulb_upper_center": Point3D(-0.875, 0.2165, 0.0),
    "bulb_lower_center": Point3D(-0.875, -0.2165, 0.0)
}


def mandelbulb_stability(point: Point3D, max_iter: int = 100, power: int = 8) -> float:
    """3D Mandelbulb stability calculation. Extended Mandelbrot to 3D space"""
    x, y, z = point.coords
    dr = 1.0
    r = 0.0
    
    for i in range(max_iter):
        r = np.sqrt(x*x + y*y + z*z)
        if r > 2:
            return i / max_iter
        
        # Convert to spherical coordinates
        theta = np.arctan2(np.sqrt(x*x + y*y), z)
        phi = np.arctan2(y, x)
        
        dr = (r ** (power - 1)) * power * dr + 1.0
        
        # Scale and rotate
        rn = r ** power
        x = rn * np.sin(theta * power) * np.cos(phi * power) + point.x
        y = rn * np.sin(theta * power) * np.sin(phi * power) + point.y
        z = rn * np.cos(theta * power) + point.z
    
    return 1.0
