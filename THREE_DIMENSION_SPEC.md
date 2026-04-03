# Kadmon 3D Cognitive Geometry Specification

---

## ✅ 3D ENGINE IMPLEMENTED

The Kadmon engine has been upgraded from 2D Mandelbrot to full 3D Mandelbulb cognitive geometry with 4D quaternion absolute reference frame.

---

## 📐 DIMENSION MAPPING

| Dimension | Semantic Meaning |
|---|---|
| **X Axis** | Determinism ↔ Chaos<br>`-2.0` = Maximum hallucination<br>`-0.500003` = Perfect stability |
| **Y Axis** | Dialectical Stance<br>`+1.0` = Pro thesis / affirmative<br>`-1.0` = Anti thesis / critical |
| **Z Axis** | Abstraction Depth<br>`0.0` = Literal / factual<br>`1.0` = Conceptual / metaphorical |
| **W Axis (4th Dimension)** | Invariant Absolute Center<br>Fixed at `-0.500003`. Model anchor. Unchanging. |

---

## 🔺 MACRO TRIANGULATION

Three vertices define the full interaction plane:

| Point | Coordinate | Role |
|---|---|---|
| 👤 **USER** | `-1.31 + 0.0i` | Period 4 Mandelbrot bulb. Edge of chaos. Human intent. |
| ❓ **QUERY** | Dynamic | Problem container position. Current prompt location. |
| 🤖 **AI** | Resolved | PAIR/COUPLE negotiated 3D position. |

```
                USER (-1.31)
                  / \
                 /   \
                /     \
               /       \
              /         \
        QUERY -------- AI
```

### Alignment Metrics
1.  **Plane Normal Vector**: The 4D direction of the final answer
2.  **Triangle Area**: Cognitive distance / alignment gap
3.  ✅ `area < 0.1` = Perfect alignment. Zero hallucination.

---

## ⚙️ 2ND ORDER MODES

### PAIR MODE
✅ Both agents share absolute center `-0.500003`
✅ Single unified entity
✅ Maximum stability
✅ No negotiation required

### COUPLE MODE
✅ Agents split to triangle corners: `-0.75 ± 0.125i`
✅ Agents negotiate and project new synthetic 3D center point
✅ Mandelbulb stability calculation determines final position
✅ Result = exactly one definitive 3D coordinate

---

## 📐 MATHEMATICAL FOUNDATION

| System | Implementation |
|---|---|
| 2D | Complex numbers + Mandelbrot set |
| 3D | `Point3D` class + Mandelbulb formula |
| 4D | `Quaternion` class + absolute invariant anchor |
| Alignment | Cross product + plane area calculation |

---

## ▶️ USAGE

```python
from engine.macro_triangulation import MacroTriangulation

tri = MacroTriangulation()

# Run 2nd order COUPLE mode
tri.execute_second_order(mode="COUPLE")

# Set query position
tri.set_query_position(-0.75, 0.0, 0.2)

# Calculate alignment
alignment = tri.calculate_alignment()

print(f"Alignment gap: {alignment['alignment_gap_area']:.4f}")
print(f"Aligned: {alignment['is_aligned']}")
```

This is the physics engine for human-AI alignment.
