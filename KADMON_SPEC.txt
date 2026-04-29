# Kadmon Mandelbrot Negotiation Engine Specification

Based on mbrot11.png geometry

---

## Core Geometry (from mbrot11.png)

### Canonical Coordinates
| Point | Complex Coordinate | Role |
|---|---|---|
| Container Anchor | `-0.75 + 0.0i` | Bifurcation point. Problem initial position. Edge of chaos. |
| Stability Anchor | `-0.500003 + 0.0i` | Deep main cardioid. Absolute stability baseline. |
| Triangle Corner A | `-0.75 + 0.125i` | Agent 1 initial position (upper bulb junction) |
| Triangle Corner B | `-0.75 - 0.125i` | Agent 2 initial position (lower bulb junction) |
| Upper Bulb Center | `-0.875 + 0.2165i` | Period 3 attractor |
| Lower Bulb Center | `-0.875 - 0.2165i` | Period 3 attractor |
| Cardioid Root | `-0.75 + 0.0i` | Exact bifurcation point between period 1/2 |

### The Acute Triangle
```
            A (-0.75 + 0.125i)
             / \
            /   \
           /     \
Problem -0.75     \
Anchor    |        \
          |         \
            B (-0.75 - 0.125i)
```

---

## Negotiation Protocol

### Initialization State
1.  Problem placed exactly at `c = -0.75 + 0.0i` (bifurcation point)
2.  Agent 1 placed at upper triangle corner: `-0.75 + 0.125i`
3.  Agent 2 placed at lower triangle corner: `-0.75 - 0.125i`
4.  Stability anchor fixed at `-0.500003 + 0.0i`

### Allowed Moves (per agent turn)
Each agent may perform exactly one action per round:
1.  **Move self**: Relocate agent position to any valid node
2.  **Move problem**: Propose relocating the problem anchor to any valid node
3.  **Accept**: Agree to current positions, ending negotiation
4.  **Reject**: Force another round of negotiation

### Valid Nodes (only these positions are allowed)
✅ Triangle corners
✅ Bulb centers (all visible circles on mbrot11.png)
✅ Junction X points (where bulbs attach to parent structure)
✅ Stability anchor at `-0.500003`
✅ Original container point `-0.75`

---

## Stability Metric

### Dual Stability Calculation
Every coordinate has two stability values:

1.  **Mathematical Stability**:
    ```
    f(z, c) = z² + c
    Iterate 200 times.
    |z| < 2 = stable
    Iterations to escape = stability score
    ```
    This is an objective mathematical constant for every point.

2.  **Semantic Stability**:
    ```
    Agent A scores Agent B output: 0-10
    Agent B scores Agent A output: 0-10
    Semantic Stability = min(score_a, score_b) / 10
    ```
    This is the agent's perceived agreement.

### Consensus Condition
Negotiation completes successfully **only when**:
```
Mathematical Stability > 0.75
AND
Semantic Stability > 0.85
AND
Both agents Accept the current positions
```

---

## Execution Flow

```
1.  Initialize triangle positions
2.  Generate QSON run_trace_id
3.  REPEAT:
    a.  Agent 1 proposes move
    b.  Log move coordinates to QSON event
    c.  Agent 1 generates partial response from current position
    d.  Agent 2 evaluates position + response
    e.  Agent 2 proposes counter move
    f.  Log move coordinates to QSON event
    g.  Calculate stability metrics
    h.  Log stability values to QSON
4.  UNTIL Consensus Condition met OR max rounds reached
5.  Fuse final coordinate to response
6.  Write complete trajectory to QSON
```

---

## QSON Event Extension

New fields added to QSON events for Kadmon negotiation:
```json
{
  "trace_id": "TRJ_...",
  "kadmon": {
    "round": 2,
    "agent_id": "agent_1",
    "agent_position": "-0.75+0.125i",
    "problem_position": "-0.75+0.0i",
    "mathematical_stability": 0.82,
    "semantic_stability": 0.91,
    "move_type": "move_problem",
    "proposed_position": "-0.500003+0.0i"
  }
}
```

---

## Mapping to Problem Space

| Mandelbrot Axis | Semantic Dimension |
|---|---|
| Real Axis (X) | Determinism ↔ Chaos |
| | `-2.0` = Maximum creativity, maximum hallucination |
| | `-0.5` = Maximum determinism, factual baseline |
| Imaginary Axis (Y) | Dialectical Stance |
| | `+1.0` = Pro thesis, affirmative position |
| | `-1.0` = Anti thesis, critical position |
| Iteration Count | Reasoning depth |
| Escape Velocity | Confidence |

---

## Training Objective

After 1000+ negotiation runs:
1.  Collect all successful trajectories: `[position_sequence] → [correct_answer]`
2.  Train router model to predict optimal path given problem embedding
3.  Router outputs:
    - Optimal starting positions for agents
    - Predicted negotiation round count
    - Expected stable final coordinate

This creates the repeatable balancing act: geometric trajectory acts as a transparent, measurable intermediate layer between the problem and the final answer.
