# Kadmon WebGL Visualization Plan

---

## ✅ BACKEND COMPLETE

FastAPI WebSocket backend implemented in `api/server.py`

Streams 60fps coordinate updates:
```json
{
  "round": 5,
  "user": [-1.31, 0.0, 0.2],
  "query": [-0.75, 0.0, 0.2],
  "ai": [-0.500003, 0.0, 0.2],
  "alignment_gap": 0.08,
  "stability": 0.92
}
```

---

## 🎨 REACT THREE FIBER IMPLEMENTATION

### Stack
- React 18
- @react-three/fiber
- @react-three/drei
- Three.js
- Mandelbulb raymarching shader

### Features
1.  Real-time raymarched Mandelbulb fractal background
2.  Smooth 3D camera controls (OrbitControls)
3.  Animated agent points flying along fractal surface
4.  Glowing alignment triangle with area indicator
5.  Particle effects for stability measurement
6.  Real-time coordinate streaming over WebSocket
7.  60fps animation loop

---

## ▶️ RUN BACKEND

```bash
cd api
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

WebSocket endpoint: `ws://localhost:8000/ws/negotiate`

---

The frontend will render the full 3D Mandelbulb set and animate agents moving along the fractal surface during negotiation, with real-time alignment visualization.
