# Kadmon 1st Order Multiplayer World Environment

A standalone online multiplayer live world environment built on the Kadmon Mandelbrot Negotiation Engine, similar to Warcraft or Counter-Strike, capable of housing thousands of entities.

## Architecture

- **Backend**: FastAPI WebSocket server for real-time state synchronization
- **Frontend**: Three.js 3D world renderer with React UI
- **Core Logic**: Kadmon negotiation system from the original project
- **Entity System**: Support for thousands of dynamic entities

## Features

✅ Multiplayer world server with WebSocket real-time updates
✅ 3D interactive world using Three.js
✅ Full Kadmon 1st order system implementation
✅ Player spawning and movement
✅ Entity management system (1000+ concurrent entities)
✅ Kadmon negotiation protocol for multi-agent systems
✅ Static anchor points from Mandelbrot set

## Prerequisites

- Python 3.10+
- Node.js 18+

## Installation

### Server Setup
```bash
cd server
pip install -r requirements.txt
```

### Client Setup
```bash
cd client
npm install
```

## Running

### Start the Backend Server
```bash
cd server
python main.py
```
The server will run on `http://localhost:8000`

### Start the Frontend Client
```bash
cd client
npm run dev
```
The client will run on `http://localhost:3000`

## Usage

1. Open `http://localhost:3000` in your browser
2. Click "Create New World" to generate a Kadmon multiplayer world
3. Enter your Player ID and Name
4. Click "Join World" to enter the 3D environment
5. Click anywhere in the 3D world to move your player

## Kadmon System Integration

This project implements the full Kadmon 1st order system from the parent repository:

- Mandelbrot set anchor points
- Mathematical stability calculations
- Multi-agent negotiation protocol
- 1st, 2nd, 3rd, and 4th order system containment

## World Entities

The world supports up to 1000 concurrent entities by default, including:
- Player avatars
- Static anchor points
- Dynamic negotiation entities
- Custom spawn points

## Configuration

### Entity Limit
Edit `server/main.py` and modify the `max_entities` parameter in the `WorldState` class:
```python
self.max_entities = 1000  # Adjust this value
```

### Server Port
Update the port in `server/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

## API Endpoints

- `GET /api/worlds` - List all active worlds
- `POST /api/worlds` - Create a new world
- `POST /api/worlds/{world_id}/join` - Join a world
- `POST /api/worlds/{world_id}/move` - Update player position
- `POST /api/worlds/{world_id}/kadmon/start` - Start Kadmon negotiation
- `POST /api/worlds/{world_id}/kadmon/move` - Agent move in negotiation
- `GET /api/worlds/{world_id}/kadmon/status` - Get negotiation status
- `WS /ws/world/{world_id}` - WebSocket for real-time world updates

## License

MIT