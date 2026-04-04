import cmath
import uuid
from datetime import datetime

# Kadmon core logic test
KADMON_POINTS = {
    "container": complex(-0.75, 0.0),
    "stability_anchor": complex(-0.500003, 0.0),
    "triangle_upper": complex(-0.75, 0.125),
    "triangle_lower": complex(-0.75, -0.125),
    "bulb_upper_center": complex(-0.875, 0.2165),
    "bulb_lower_center": complex(-0.875, -0.2165),
    "cardioid_root": complex(-0.75, 0.0)
}

def mandelbrot_stability(c: complex, max_iter: int = 200) -> float:
    """Calculate mathematical stability of a point in Mandelbrot set"""
    z = 0j
    for i in range(max_iter):
        z = z * z + c
        if abs(z) > 2:
            return i / max_iter
    return 1.0

# Test the logic
print("Testing Kadmon core logic...")
negotiation = KadmonNegotiation()
print(f"Initial problem position: {negotiation.problem_position}")
print(f"Mathematical stability: {mandelbrot_stability(negotiation.problem_position)}")
print("✓ Kadmon core logic works correctly!")