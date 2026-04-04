"""
Kadmon 1st Order Multiplayer World Server
Implements: World management, Player/LLM entity registry,
            Kadmon negotiation, System-of-Systems plugin rack.
"""

import asyncio
import json
import uuid
import cmath
import random
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# ---------------------------------------------------------------------------
# Kadmon Core (embedded — no external import needed)
# ---------------------------------------------------------------------------
KADMON_POINTS = {
    "container":       complex(-0.75,      0.0),
    "stability_anchor":complex(-0.500003,  0.0),
    "triangle_upper":  complex(-0.75,      0.125),
    "triangle_lower":  complex(-0.75,     -0.125),
    "bulb_upper_center":complex(-0.875,    0.2165),
    "bulb_lower_center":complex(-0.875,   -0.2165),
    "cardioid_root":   complex(-0.75,      0.0),
}
VALID_NODES = list(KADMON_POINTS.values())

KADMON_SCHEMA_HEADER = """\
KADMON SCHEMA HEADER:
1st Ordered Dimension: Time         — high preference for X axis
2nd Ordered Dimension: Stance       — high preference for Y axis
3rd Ordered Dimension: Abstraction  — high preference for Z axis
4th Ordered Dimension: INVARIANT CENTER = C = -0.500003

You are operating within the Kadmon Runtime Environment.
Your center point is fixed at C = -0.500003.
All positions are relative to this invariant center point.
"""

def mandelbrot_stability(c: complex, max_iter: int = 200) -> float:
    z = 0j
    for i in range(max_iter):
        z = z * z + c
        if abs(z) > 2:
            return i / max_iter
    return 1.0

class KadmonNegotiation:
    def __init__(self):
        self.round = 0
        self.problem_position  = KADMON_POINTS["container"]
        self.agent1_position   = KADMON_POINTS["triangle_upper"]
        self.agent2_position   = KADMON_POINTS["triangle_lower"]
        self.history: List[Dict] = []
        self.complete = False
        self.agreed_position: Optional[complex] = None

    def agent_move(self, agent_id: str, new_position: complex):
        if new_position not in VALID_NODES:
            raise ValueError(f"Invalid position: {new_position}")
        if agent_id == "agent_1":
            self.agent1_position = new_position
        elif agent_id == "agent_2":
            self.agent2_position = new_position
        self._log_move(agent_id, "move_self", new_position)

    def propose_problem_move(self, agent_id: str, new_position: complex):
        if new_position not in VALID_NODES:
            raise ValueError(f"Invalid position: {new_position}")
        self.problem_position = new_position
        self._log_move(agent_id, "move_problem", new_position)

    def calculate_stability(self) -> Dict:
        return {
            "mathematical": mandelbrot_stability(self.problem_position),
            "problem_position": {"real": self.problem_position.real, "imag": self.problem_position.imag},
            "agent1_position":  {"real": self.agent1_position.real,  "imag": self.agent1_position.imag},
            "agent2_position":  {"real": self.agent2_position.real,  "imag": self.agent2_position.imag},
            "round": self.round,
        }

    def check_consensus(self, semantic_stability: float) -> bool:
        ms = mandelbrot_stability(self.problem_position)
        if ms > 0.75 and semantic_stability > 0.85:
            self.complete = True
            self.agreed_position = self.problem_position
            return True
        return False

    def _log_move(self, agent_id, move_type, position):
        self.round += 1
        self.history.append({
            "trace_id":        f"TRJ_{uuid.uuid4()}",
            "round":           self.round,
            "agent_id":        agent_id,
            "move_type":       move_type,
            "position":        {"real": position.real, "imag": position.imag},
            "problem_position":{"real": self.problem_position.real, "imag": self.problem_position.imag},
            "timestamp":       datetime.utcnow().isoformat() + "Z",
            "stability":       self.calculate_stability(),
        })


# ---------------------------------------------------------------------------
# System-of-Systems Plugin Rack  (VST-style)
# ---------------------------------------------------------------------------
BUILTIN_SYSTEM_MANIFESTS: List[Dict] = [
    {
        "system_id": "kadmon_negotiation",
        "name":      "Kadmon Negotiation",
        "order":     1,
        "description": "1st Order Mandelbrot negotiation protocol between two agents.",
        "params":    {"max_rounds": 20, "consensus_threshold": 0.85},
    },
    {
        "system_id": "mcp_memory",
        "name":      "MCP Memory Server",
        "order":     4,
        "description": "4th Order key-value memory context server.",
        "params":    {},
    },
    {
        "system_id": "nych_encoder",
        "name":      "NYCH Encoder",
        "order":     5,
        "description": "5th Order gestalt phonetic encoder.",
        "params":    {},
    },
    {
        "system_id": "mobius_tmt",
        "name":      "Möbius TMT",
        "order":     4,
        "description": "4th Order triadic Möbius transport system.",
        "params":    {},
    },
    {
        "system_id": "pair_config",
        "name":      "PAIR Config",
        "order":     2,
        "description": "2nd Order dual-agent PAIR configuration.",
        "params":    {"alignment_threshold": 0.75},
    },
    {
        "system_id": "couple_config",
        "name":      "COUPLE Config",
        "order":     2,
        "description": "2nd Order projective cross-validation COUPLE system.",
        "params":    {"cross_validate": True},
    },
    {
        "system_id": "training_router",
        "name":      "Training Router",
        "order":     4,
        "description": "4th Order ML router trained on successful negotiation trajectories.",
        "params":    {},
    },
    {
        "system_id": "llm_gpt",
        "name":      "LLM: GPT",
        "order":     3,
        "description": "3rd Order OpenAI GPT language model agent.",
        "params":    {"model": "gpt-4o", "temperature": 0.7},
    },
    {
        "system_id": "llm_claude",
        "name":      "LLM: Claude",
        "order":     3,
        "description": "3rd Order Anthropic Claude language model agent.",
        "params":    {"model": "claude-3-5-sonnet-20241022", "temperature": 0.7},
    },
    {
        "system_id": "llm_gemini",
        "name":      "LLM: Gemini",
        "order":     3,
        "description": "3rd Order Google Gemini language model agent.",
        "params":    {"model": "gemini-pro", "temperature": 0.7},
    },
    {
        "system_id": "llm_grok",
        "name":      "LLM: Grok",
        "order":     3,
        "description": "3rd Order xAI Grok language model agent.",
        "params":    {"model": "grok-1", "temperature": 0.7},
    },
]

class SystemInstance:
    """Live instance of an installed system in the plugin rack."""
    def __init__(self, manifest: Dict, config: Optional[Dict] = None):
        self.instance_id = f"SYS_{uuid.uuid4()}"
        self.system_id   = manifest["system_id"]
        self.name        = manifest["name"]
        self.order       = manifest["order"]
        self.description = manifest["description"]
        self.params      = {**manifest.get("params", {}), **(config or {})}
        self.status      = "installed"   # installed | enabled | disabled | error
        self.installed_at = datetime.utcnow().isoformat() + "Z"
        self.enabled_at   = None
        self.runtime_data: Dict = {}

    def enable(self):
        self.status     = "enabled"
        self.enabled_at = datetime.utcnow().isoformat() + "Z"
        self.runtime_data["started"] = True

    def disable(self):
        self.status = "disabled"
        self.runtime_data["started"] = False

    def to_dict(self) -> Dict:
        return {
            "instance_id":  self.instance_id,
            "system_id":    self.system_id,
            "name":         self.name,
            "order":        self.order,
            "description":  self.description,
            "params":       self.params,
            "status":       self.status,
            "installed_at": self.installed_at,
            "enabled_at":   self.enabled_at,
            "runtime_data": self.runtime_data,
        }


class SystemRack:
    """1st Order System-of-Systems plugin rack (VST-style)."""
    def __init__(self):
        self.manifests: Dict[str, Dict] = {m["system_id"]: m for m in BUILTIN_SYSTEM_MANIFESTS}
        self.instances: Dict[str, SystemInstance] = {}
        self._events: Dict[str, List] = {}

    # ------------------------------------------------------------------
    def available(self) -> List[Dict]:
        return list(self.manifests.values())

    def install(self, system_id: str, config: Optional[Dict] = None) -> SystemInstance:
        if system_id not in self.manifests:
            raise ValueError(f"Unknown system: {system_id}")
        inst = SystemInstance(self.manifests[system_id], config)
        self.instances[inst.instance_id] = inst
        self._emit("install", inst.to_dict())
        return inst

    def enable(self, instance_id: str) -> SystemInstance:
        inst = self._get(instance_id)
        inst.enable()
        self._emit("enable", inst.to_dict())
        return inst

    def disable(self, instance_id: str) -> SystemInstance:
        inst = self._get(instance_id)
        inst.disable()
        self._emit("disable", inst.to_dict())
        return inst

    def uninstall(self, instance_id: str):
        inst = self._get(instance_id)
        if inst.status == "enabled":
            inst.disable()
        del self.instances[instance_id]
        self._emit("uninstall", {"instance_id": instance_id})

    def get_instances(self, order: Optional[int] = None) -> List[Dict]:
        insts = list(self.instances.values())
        if order is not None:
            insts = [i for i in insts if i.order == order]
        return [i.to_dict() for i in insts]

    def snapshot(self) -> Dict:
        return {
            "available": self.available(),
            "instances":  self.get_instances(),
        }

    # ------------------------------------------------------------------
    def subscribe(self, event: str, callback):
        self._events.setdefault(event, []).append(callback)

    def _emit(self, event: str, data: Dict):
        for cb in self._events.get(event, []) + self._events.get("*", []):
            try:
                cb(event, data)
            except Exception:
                pass

    def _get(self, instance_id: str) -> SystemInstance:
        if instance_id not in self.instances:
            raise ValueError(f"Instance not found: {instance_id}")
        return self.instances[instance_id]


# ---------------------------------------------------------------------------
# Player / LLM Entity Model
# ---------------------------------------------------------------------------
def _pos_to_dict(c: complex) -> Dict:
    return {"real": c.real, "imag": c.imag, "z": 0.0}

class PlayerEntity:
    """Represents a human player or LLM agent in the world."""
    VALID_TYPES = {"human", "llm_gpt", "llm_claude", "llm_gemini", "llm_grok", "llm_custom"}

    def __init__(self, player_id: str, name: str, entity_type: str = "human",
                 model: Optional[str] = None, system_prompt: Optional[str] = None):
        self.player_id    = player_id
        self.name         = name
        self.entity_type  = entity_type if entity_type in self.VALID_TYPES else "human"
        self.model        = model
        self.system_prompt= system_prompt or KADMON_SCHEMA_HEADER
        self.entity_id    = f"ENT_{uuid.uuid4()}"
        self.position     = KADMON_POINTS["container"]  # spawn at container
        self.connected_at = datetime.utcnow().isoformat() + "Z"
        self.last_seen    = datetime.utcnow().isoformat() + "Z"
        self.is_active    = True
        self.negotiation_role: Optional[str] = None  # agent_1 / agent_2
        self.chat_history: List[Dict] = []

    # ------------------------------------------------------------------
    def move(self, real: float, imag: float, z: float = 0.0):
        self.position = complex(real, imag)
        self.last_seen = datetime.utcnow().isoformat() + "Z"

    def send_message(self, text: str) -> Dict:
        """Human turn: store message, return record."""
        msg = {
            "id":        f"MSG_{uuid.uuid4()}",
            "player_id": self.player_id,
            "role":      "user",
            "content":   text,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "position":  _pos_to_dict(self.position),
        }
        self.chat_history.append(msg)
        return msg

    def llm_respond(self, context: str) -> Dict:
        """LLM turn: generate a mock (or real) response."""
        if self.entity_type == "human":
            raise ValueError("Human players do not auto-respond")

        # Build prompt
        prompt = f"{self.system_prompt}\n\nCONTEXT:\n{context}\n\nRESPOND:"

        # Attempt real model call — fall back to mock
        response_text = _call_llm_backend(self.entity_type, self.model, prompt)

        msg = {
            "id":        f"MSG_{uuid.uuid4()}",
            "player_id": self.player_id,
            "role":      "assistant",
            "content":   response_text,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "position":  _pos_to_dict(self.position),
            "model":     self.model,
        }
        self.chat_history.append(msg)
        return msg

    def to_dict(self) -> Dict:
        return {
            "player_id":        self.player_id,
            "name":             self.name,
            "entity_type":      self.entity_type,
            "model":            self.model,
            "entity_id":        self.entity_id,
            "position":         _pos_to_dict(self.position),
            "connected_at":     self.connected_at,
            "last_seen":        self.last_seen,
            "is_active":        self.is_active,
            "negotiation_role": self.negotiation_role,
            "message_count":    len(self.chat_history),
        }


def _call_llm_backend(entity_type: str, model: Optional[str], prompt: str) -> str:
    """Route to real LLM SDK or return a deterministic mock."""
    try:
        if entity_type == "llm_gpt":
            import openai
            client = openai.OpenAI()
            resp = client.chat.completions.create(
                model=model or "gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=256,
            )
            return resp.choices[0].message.content

        if entity_type == "llm_claude":
            import anthropic
            client = anthropic.Anthropic()
            resp = client.messages.create(
                model=model or "claude-3-5-sonnet-20241022",
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text

        if entity_type == "llm_gemini":
            import google.generativeai as genai
            m = genai.GenerativeModel(model or "gemini-pro")
            resp = m.generate_content(prompt)
            return resp.text

    except Exception as e:
        pass  # Fall through to mock

    # Deterministic mock
    random.seed(hash(prompt) % (2**32))
    confidence = round(random.uniform(0.6, 0.99), 3)
    return f"[{entity_type.upper()} MOCK] confidence={confidence} | Kadmon position evaluated. Stability metric assessed."


# ---------------------------------------------------------------------------
# World State
# ---------------------------------------------------------------------------
class WorldEntity:
    """Non-player world object."""
    def __init__(self, etype: str, position: complex, label: str = ""):
        self.entity_id   = f"ENT_{uuid.uuid4()}"
        self.entity_type = etype
        self.position    = position
        self.label       = label
        self.created_at  = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict:
        return {
            "entity_id":   self.entity_id,
            "entity_type": self.entity_type,
            "position":    _pos_to_dict(self.position),
            "label":       self.label,
            "created_at":  self.created_at,
        }


class WorldState:
    def __init__(self, world_id: str, name: str = ""):
        self.world_id    = world_id
        self.name        = name or f"Kadmon World {world_id[-8:]}"
        self.created_at  = datetime.utcnow().isoformat() + "Z"
        self.players:    Dict[str, PlayerEntity]  = {}
        self.entities:   Dict[str, WorldEntity]   = {}
        self.kadmon:     Optional[KadmonNegotiation] = None
        self.rack:       SystemRack = SystemRack()
        self.chat_log:   List[Dict] = []
        self.max_entities = 2000

        # Pre-seed canonical Kadmon anchor points
        for name_key, cpt in KADMON_POINTS.items():
            if name_key in ("container", "stability_anchor",
                            "bulb_upper_center", "bulb_lower_center",
                            "triangle_upper", "triangle_lower"):
                we = WorldEntity("kadmon_anchor", cpt, name_key)
                self.entities[we.entity_id] = we

    # ------------------------------------------------------------------
    def add_player(self, player: PlayerEntity):
        self.players[player.player_id] = player

    def remove_player(self, player_id: str):
        if player_id in self.players:
            self.players[player_id].is_active = False

    def spawn_entity(self, etype: str, position: complex, label: str = "") -> WorldEntity:
        if len(self.entities) >= self.max_entities:
            raise ValueError("World entity cap reached")
        we = WorldEntity(etype, position, label)
        self.entities[we.entity_id] = we
        return we

    def start_negotiation(self) -> KadmonNegotiation:
        self.kadmon = KadmonNegotiation()
        return self.kadmon

    def to_dict(self) -> Dict:
        return {
            "world_id":    self.world_id,
            "name":        self.name,
            "created_at":  self.created_at,
            "player_count": len([p for p in self.players.values() if p.is_active]),
            "entity_count": len(self.entities),
            "kadmon_active": self.kadmon is not None and not self.kadmon.complete,
            "players":  [p.to_dict() for p in self.players.values()],
            "entities": [e.to_dict() for e in self.entities.values()],
            "chat_log": self.chat_log[-50:],   # last 50 messages
            "rack":     self.rack.snapshot(),
        }


# ---------------------------------------------------------------------------
# Connection Manager (WebSocket broadcast)
# ---------------------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self._conns: Dict[str, List[WebSocket]] = {}  # world_id -> [ws, ...]

    async def connect(self, ws: WebSocket, world_id: str):
        await ws.accept()
        self._conns.setdefault(world_id, []).append(ws)

    def disconnect(self, ws: WebSocket, world_id: str):
        self._conns.get(world_id, []).remove(ws)

    async def broadcast(self, world_id: str, msg: Dict):
        dead = []
        for ws in self._conns.get(world_id, []):
            try:
                await ws.send_text(json.dumps(msg))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._conns[world_id].remove(ws)


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(title="Kadmon 1st Order Multiplayer World")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

worlds:  Dict[str, WorldState]  = {}
manager: ConnectionManager      = ConnectionManager()


# ---------------------------------------------------------------------------
# Pydantic request models
# ---------------------------------------------------------------------------
class CreateWorldReq(BaseModel):
    name: Optional[str] = None

class AddPlayerReq(BaseModel):
    player_id:     str
    name:          str
    entity_type:   str = "human"   # human | llm_gpt | llm_claude | llm_gemini | llm_grok
    model:         Optional[str] = None
    system_prompt: Optional[str] = None

class MovePlayerReq(BaseModel):
    player_id: str
    real:      float
    imag:      float
    z:         float = 0.0

class ChatReq(BaseModel):
    player_id: str
    message:   str

class LLMRespondReq(BaseModel):
    player_id: str   # must be an LLM entity
    context:   str

class KadmonMoveReq(BaseModel):
    agent_id:     str
    point_name:   str   # key from KADMON_POINTS
    move_type:    str = "move_self"  # move_self | move_problem

class InstallSystemReq(BaseModel):
    system_id: str
    config:    Optional[Dict] = None

class SystemActionReq(BaseModel):
    instance_id: str

class SpawnEntityReq(BaseModel):
    entity_type: str
    real:        float
    imag:        float
    z:           float = 0.0
    label:       str = ""


# ---------------------------------------------------------------------------
# Helper: get world or raise
# ---------------------------------------------------------------------------
def _world(world_id: str) -> WorldState:
    if world_id not in worlds:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"World {world_id} not found")
    return worlds[world_id]


# ---------------------------------------------------------------------------
# World endpoints
# ---------------------------------------------------------------------------
@app.get("/api/worlds")
def list_worlds():
    return [{"world_id": w.world_id, "name": w.name,
             "players": len(w.players), "entities": len(w.entities)}
            for w in worlds.values()]


@app.post("/api/worlds")
def create_world(req: CreateWorldReq):
    wid = f"WORLD_{uuid.uuid4()}"
    w = WorldState(wid, req.name)
    worlds[wid] = w
    return w.to_dict()


@app.get("/api/worlds/{world_id}")
def get_world(world_id: str):
    return _world(world_id).to_dict()


@app.delete("/api/worlds/{world_id}")
def delete_world(world_id: str):
    _world(world_id)
    del worlds[world_id]
    return {"deleted": world_id}


# ---------------------------------------------------------------------------
# Player / LLM endpoints
# ---------------------------------------------------------------------------
@app.get("/api/player_types")
def get_player_types():
    """Return available player/LLM types."""
    return {
        "types": [
            {"type": "human",      "label": "Human Player",  "needs_model": False},
            {"type": "llm_gpt",    "label": "GPT Agent",     "needs_model": True,  "default_model": "gpt-4o"},
            {"type": "llm_claude", "label": "Claude Agent",  "needs_model": True,  "default_model": "claude-3-5-sonnet-20241022"},
            {"type": "llm_gemini", "label": "Gemini Agent",  "needs_model": True,  "default_model": "gemini-pro"},
            {"type": "llm_grok",   "label": "Grok Agent",    "needs_model": True,  "default_model": "grok-1"},
            {"type": "llm_custom", "label": "Custom LLM",    "needs_model": True,  "default_model": ""},
        ]
    }


@app.post("/api/worlds/{world_id}/players")
async def add_player(world_id: str, req: AddPlayerReq):
    w = _world(world_id)
    if req.player_id in w.players:
        return {"error": "player_id already exists in this world"}, 400

    player = PlayerEntity(
        player_id=req.player_id,
        name=req.name,
        entity_type=req.entity_type,
        model=req.model,
        system_prompt=req.system_prompt,
    )
    w.add_player(player)

    event = {
        "type":      "player_joined",
        "player":    player.to_dict(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    await manager.broadcast(world_id, event)
    return player.to_dict()


@app.get("/api/worlds/{world_id}/players")
def list_players(world_id: str):
    w = _world(world_id)
    return [p.to_dict() for p in w.players.values()]


@app.delete("/api/worlds/{world_id}/players/{player_id}")
async def remove_player(world_id: str, player_id: str):
    w = _world(world_id)
    w.remove_player(player_id)
    await manager.broadcast(world_id, {
        "type": "player_left", "player_id": player_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })
    return {"removed": player_id}


@app.post("/api/worlds/{world_id}/players/{player_id}/move")
async def move_player(world_id: str, player_id: str, req: MovePlayerReq):
    w = _world(world_id)
    if player_id not in w.players:
        from fastapi import HTTPException
        raise HTTPException(404, "Player not found")
    w.players[player_id].move(req.real, req.imag, req.z)
    pos = _pos_to_dict(w.players[player_id].position)
    await manager.broadcast(world_id, {
        "type": "player_moved", "player_id": player_id,
        "position": pos, "timestamp": datetime.utcnow().isoformat() + "Z",
    })
    return {"player_id": player_id, "position": pos}


@app.post("/api/worlds/{world_id}/players/{player_id}/chat")
async def player_chat(world_id: str, player_id: str, req: ChatReq):
    """Human player sends a chat message."""
    w = _world(world_id)
    if player_id not in w.players:
        from fastapi import HTTPException
        raise HTTPException(404, "Player not found")

    msg = w.players[player_id].send_message(req.message)
    w.chat_log.append(msg)
    await manager.broadcast(world_id, {"type": "chat", "message": msg})
    return msg


@app.post("/api/worlds/{world_id}/players/{player_id}/respond")
async def llm_respond(world_id: str, player_id: str, req: LLMRespondReq):
    """Trigger an LLM agent to respond to a given context."""
    w = _world(world_id)
    if player_id not in w.players:
        from fastapi import HTTPException
        raise HTTPException(404, "Player not found")

    player = w.players[player_id]
    if player.entity_type == "human":
        from fastapi import HTTPException
        raise HTTPException(400, "Human players cannot auto-respond")

    msg = player.llm_respond(req.context)
    w.chat_log.append(msg)
    await manager.broadcast(world_id, {"type": "chat", "message": msg})
    return msg


# ---------------------------------------------------------------------------
# Kadmon Negotiation endpoints
# ---------------------------------------------------------------------------
@app.post("/api/worlds/{world_id}/kadmon/start")
async def start_negotiation(world_id: str):
    w = _world(world_id)
    neg = w.start_negotiation()
    state = neg.calculate_stability()
    await manager.broadcast(world_id, {"type": "kadmon_started", "state": state})
    return {"started": True, "state": state}


@app.post("/api/worlds/{world_id}/kadmon/move")
async def kadmon_move(world_id: str, req: KadmonMoveReq):
    w = _world(world_id)
    if not w.kadmon:
        from fastapi import HTTPException
        raise HTTPException(400, "No active negotiation — POST /kadmon/start first")

    if req.point_name not in KADMON_POINTS:
        from fastapi import HTTPException
        raise HTTPException(400, f"Unknown point: {req.point_name}. Valid: {list(KADMON_POINTS.keys())}")

    pt = KADMON_POINTS[req.point_name]
    if req.move_type == "move_problem":
        w.kadmon.propose_problem_move(req.agent_id, pt)
    else:
        w.kadmon.agent_move(req.agent_id, pt)

    stability = w.kadmon.calculate_stability()
    await manager.broadcast(world_id, {
        "type": "kadmon_move",
        "agent_id": req.agent_id,
        "move_type": req.move_type,
        "point_name": req.point_name,
        "stability": stability,
    })
    return {"stability": stability, "history_length": len(w.kadmon.history)}


@app.get("/api/worlds/{world_id}/kadmon/status")
def kadmon_status(world_id: str):
    w = _world(world_id)
    if not w.kadmon:
        return {"active": False}
    s = w.kadmon.calculate_stability()
    s["active"]   = not w.kadmon.complete
    s["complete"]  = w.kadmon.complete
    s["agreed_position"] = (
        _pos_to_dict(w.kadmon.agreed_position) if w.kadmon.agreed_position else None
    )
    s["valid_points"] = {k: {"real": v.real, "imag": v.imag} for k, v in KADMON_POINTS.items()}
    return s


@app.post("/api/worlds/{world_id}/kadmon/run")
async def kadmon_auto_run(world_id: str):
    """Auto-run negotiation: assign LLM players as agents and step through rounds."""
    w = _world(world_id)
    if not w.kadmon:
        w.start_negotiation()

    llm_players = [p for p in w.players.values() if p.entity_type != "human"]
    if len(llm_players) < 2:
        from fastapi import HTTPException
        raise HTTPException(400, "Need at least 2 LLM players for auto-run")

    llm_players[0].negotiation_role = "agent_1"
    llm_players[1].negotiation_role = "agent_2"

    results = []
    for round_num in range(min(20, w.kadmon.round + 10)):
        pts = list(KADMON_POINTS.values())
        # Agent 1 moves
        pt1 = random.choice(pts)
        context1 = (f"Round {round_num}. Problem at {w.kadmon.problem_position}. "
                    f"You are agent_1. Propose your next move.")
        resp1 = llm_players[0].llm_respond(context1)
        w.kadmon.agent_move("agent_1", pt1)

        # Agent 2 responds
        pt2 = random.choice(pts)
        context2 = (f"Round {round_num}. Agent 1 said: {resp1['content'][:80]}. "
                    f"You are agent_2. Counter-propose.")
        resp2 = llm_players[1].llm_respond(context2)
        w.kadmon.agent_move("agent_2", pt2)

        stability = w.kadmon.calculate_stability()
        results.append({"round": round_num, "stability": stability})

        if w.kadmon.check_consensus(0.87):
            break

    await manager.broadcast(world_id, {"type": "kadmon_auto_run_complete", "results": results})
    return {"rounds": len(results), "complete": w.kadmon.complete, "results": results}


# ---------------------------------------------------------------------------
# System-of-Systems / Plugin Rack endpoints
# ---------------------------------------------------------------------------
@app.get("/api/worlds/{world_id}/systems/available")
def systems_available(world_id: str):
    w = _world(world_id)
    return w.rack.available()


@app.get("/api/worlds/{world_id}/systems")
def systems_list(world_id: str):
    w = _world(world_id)
    return w.rack.get_instances()


@app.post("/api/worlds/{world_id}/systems/install")
async def systems_install(world_id: str, req: InstallSystemReq):
    w = _world(world_id)
    inst = w.rack.install(req.system_id, req.config)
    await manager.broadcast(world_id, {"type": "system_installed", "system": inst.to_dict()})
    return inst.to_dict()


@app.post("/api/worlds/{world_id}/systems/{instance_id}/enable")
async def systems_enable(world_id: str, instance_id: str):
    w = _world(world_id)
    inst = w.rack.enable(instance_id)
    await manager.broadcast(world_id, {"type": "system_enabled", "system": inst.to_dict()})
    return inst.to_dict()


@app.post("/api/worlds/{world_id}/systems/{instance_id}/disable")
async def systems_disable(world_id: str, instance_id: str):
    w = _world(world_id)
    inst = w.rack.disable(instance_id)
    await manager.broadcast(world_id, {"type": "system_disabled", "system": inst.to_dict()})
    return inst.to_dict()


@app.delete("/api/worlds/{world_id}/systems/{instance_id}")
async def systems_uninstall(world_id: str, instance_id: str):
    w = _world(world_id)
    w.rack.uninstall(instance_id)
    await manager.broadcast(world_id, {"type": "system_uninstalled", "instance_id": instance_id})
    return {"uninstalled": instance_id}


# ---------------------------------------------------------------------------
# World entity spawn
# ---------------------------------------------------------------------------
@app.post("/api/worlds/{world_id}/entities")
def spawn_entity(world_id: str, req: SpawnEntityReq):
    w = _world(world_id)
    ent = w.spawn_entity(req.entity_type, complex(req.real, req.imag), req.label)
    return ent.to_dict()


@app.get("/api/worlds/{world_id}/entities")
def list_entities(world_id: str):
    w = _world(world_id)
    return [e.to_dict() for e in w.entities.values()]


# ---------------------------------------------------------------------------
# WebSocket: real-time world stream
# ---------------------------------------------------------------------------
@app.websocket("/ws/world/{world_id}")
async def ws_world(ws: WebSocket, world_id: str):
    await manager.connect(ws, world_id)
    try:
        # Send immediate snapshot on connect
        if world_id in worlds:
            await ws.send_text(json.dumps({
                "type": "snapshot",
                "world": worlds[world_id].to_dict(),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }))
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            action = msg.get("action")

            if action == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))

            elif action == "snapshot" and world_id in worlds:
                await ws.send_text(json.dumps({
                    "type": "snapshot",
                    "world": worlds[world_id].to_dict(),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }))

    except WebSocketDisconnect:
        manager.disconnect(ws, world_id)


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------
@app.get("/api/kadmon/points")
def get_kadmon_points():
    """Return all canonical Kadmon coordinate points."""
    return {k: {"real": v.real, "imag": v.imag} for k, v in KADMON_POINTS.items()}


@app.get("/health")
def health():
    return {"status": "ok", "worlds": len(worlds), "timestamp": datetime.utcnow().isoformat() + "Z"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
