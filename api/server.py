#!/usr/bin/env python3
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.macro_triangulation import MacroTriangulation
from engine.mobius import TriadicMobiusTransport, CANONICAL_MOS
from engine.model_adapter import call_model
from engine.environment import KadmonEnvironment
from engine.kadmon import KADMON_POINTS

app = FastAPI(
    title="Kadmon Backend API",
    description="Kadmon System of Systems — 1st Order Runtime Environment. Connect via ws://127.0.0.1:8000/ws/negotiate",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1st Order: Global KadmonEnvironment — outermost container for all systems
kadmon_env = KadmonEnvironment()

@app.on_event("startup")
async def startup_event():
    """Initialize the 1st order Kadmon Runtime Environment on server start."""
    kadmon_env.start()

import httpx
from pydantic import BaseModel

async def fetch_llm(url: str, prompt: str, agent_id: str = None):
    """
    LLM call passthrough.
    - If url is provided: POST to external endpoint directly.
    - If url is empty and agent_id is provided: route through kadmon_env.call_llm()
      which enforces the KADMON SCHEMA HEADER and AGENT marker.
    - If url is empty and no agent_id: fall back to bare call_model().
    """
    try:
        if url:
            async with httpx.AsyncClient() as client:
                payload = {"messages": [{"role": "user", "content": prompt}]}
                resp = await client.post(url, json=payload, timeout=10.0)
                data = resp.json()
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
                elif "response" in data:
                    return data["response"]
                return resp.text
        elif agent_id:
            # Schema-enforced call through the 1st order environment
            return str(kadmon_env.call_llm(agent_id, prompt))
        else:
            return str(call_model(prompt))
    except Exception as e:
        label = url if url else (agent_id or "unknown")
        return f"[ERROR CALLING AGENT {label} for prompt {prompt[:20]}]: {str(e)}... confidence=0.5"


class AgentPrompt(BaseModel):
    url: str = ""
    prompt: str

@app.post("/api/prompt")
async def single_prompt(req: AgentPrompt):
    resp = await fetch_llm(req.url, req.prompt)
    return {"response": resp}


# ---------------------------------------------------------------------------
# Mandelbrot diagram canonical negotiation positions
# ---------------------------------------------------------------------------

NEGOTIATION_POSITIONS = {
    "container":         (-0.75,    0.0),
    "triangle_upper":    (-0.75,    0.125),
    "triangle_lower":    (-0.75,   -0.125),
    "bulb_upper_center": (-0.875,   0.2165),
    "bulb_lower_center": (-0.875,  -0.2165),
    "stability_anchor":  (-0.500003, 0.0),
    "user_anchor":       (-1.31,    0.0),
}

# Agent path sequences through the diagram
_AGENT1_PATH = ["triangle_upper", "container", "stability_anchor"]
_AGENT2_PATH = ["triangle_lower", "container", "stability_anchor"]


# ---------------------------------------------------------------------------
# 2nd Order Session — PAIR / COUPLE operating inside the 1st order environment
# ---------------------------------------------------------------------------

class KadmonSession:
    def __init__(self):
        self.tri = MacroTriangulation()
        self.running = False
        self.agents = []  # list of agent dicts from payload
        self.user_prompt = ""
        self.mode = "PAIR"
        self.pair = None
        # IU (Intelligence Unit) starts at KADMON_POINTS["container"] = (-0.75, 0.0, 0.0)
        iu_start = KADMON_POINTS["container"]
        self.iu_position = [iu_start.real, iu_start.imag, 0.0]

    def init_pair(self, agents: list, mode: str = "PAIR"):
        """Create the 2nd order PAIR/COUPLE inside the 1st order KadmonEnvironment.

        Registers every agent via kadmon_env.register_llm() only if not already
        registered, preventing unbounded growth of the third_order list across
        multiple negotiation rounds on the same WebSocket session.
        The first two agents form the PAIR/COUPLE anchor; additional agents
        are registered as additional 3rd order systems.
        """
        self.mode = mode

        # Register all agents in the 1st order environment (skip already-registered)
        already_registered = {a['id'] for a in kadmon_env.contained_systems.get("third_order", [])}
        for agent in agents:
            if agent['id'] not in already_registered:
                kadmon_env.register_llm(agent['model'], agent['id'])

        # Create the 2nd order pair using the first two agents as anchors
        if len(agents) >= 2:
            self.pair = kadmon_env.create_pair(agents[0]['id'], agents[1]['id'], mode)
        elif len(agents) == 1:
            self.pair = kadmon_env.create_pair(agents[0]['id'], agents[0]['id'], mode)

    async def run_negotiation(self):
        self.running = True
        import hashlib
        import re

        def map_text_to_z(text):
            match = re.search(r'confidence=([\d\.]+)', text)
            if match:
                return float(match.group(1))
            h = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
            return (h % 1000) / 1000.0

        for round_num in range(20):
            if not self.running:
                break

            # Build prompts and fetch responses for ALL registered agents
            responses = []
            for agent in self.agents:
                prompt = (
                    f"Kadmon Context: {self.user_prompt}\n"
                    f"Round {round_num}. {agent['name']} [{agent['id']}], process from your anchor position."
                )
                resp = await fetch_llm(agent.get('url', ''), prompt, agent_id=agent['id'])
                responses.append(resp)

            # Map ALL agent responses to z-values
            z_values = [map_text_to_z(r) for r in responses]

            z1 = z_values[0] if len(z_values) > 0 else 0.5
            z2 = z_values[1] if len(z_values) > 1 else z1
            z_avg = sum(z_values) / len(z_values) if z_values else 0.5

            # Execute physical engine using true LLM data
            if self.mode == "PAIR" and len(self.agents) == 2:
                self.tri.execute_second_order(mode="PAIR", agent1_z=z1, agent2_z=z2)
            else:
                self.tri.execute_second_order(mode="COUPLE", agent1_z=z_avg, agent2_z=z_avg)

            alignment = self.tri.calculate_alignment()

            # Advance IU position along X-axis proportional to round progress
            # IU starts at container (-0.75, 0.0, 0.0) and moves toward center -0.500003
            iu_x = -0.75 + (round_num / 20.0) * (-0.500003 - (-0.75))
            self.iu_position = [
                round(iu_x, 6),
                0.0,
                round(z_avg, 6),
            ]

            # Compute negotiation positions for agent_1 and agent_2 based on round progress
            pos1_key = _AGENT1_PATH[round_num % len(_AGENT1_PATH)]
            pos2_key = _AGENT2_PATH[round_num % len(_AGENT2_PATH)]
            pos1_xy = NEGOTIATION_POSITIONS[pos1_key]
            pos2_xy = NEGOTIATION_POSITIONS[pos2_key]

            yield {
                "round": round_num,
                "user": [self.tri.user_point.x, self.tri.user_point.y, self.tri.user_point.z],
                "query": [self.tri.query_point.x, self.tri.query_point.y, self.tri.query_point.z],
                "ai": [self.tri.ai_resolved_point.x, self.tri.ai_resolved_point.y, self.tri.ai_resolved_point.z],
                "alignment_gap": alignment['alignment_gap_area'],
                "stability": alignment['mandelbulb_stability'],
                "log": "Agent positions derived directly from LLM text hashing and confidence.",
                "agent_responses": {agent['id']: resp for agent, resp in zip(self.agents, responses)},
                # Backwards compatibility — first two agents
                "agent1_resp": responses[0] if len(responses) > 0 else "",
                "agent2_resp": responses[1] if len(responses) > 1 else "",
                # Kadmon architecture fields
                "iu": self.iu_position,
                "center": [-0.500003, 0.0, 0.0],
                "mode": self.mode,
                # Per-agent positions in the Mandelbrot geometry
                "negotiation_positions": {
                    "agent_1": list(pos1_xy) + [z1],
                    "agent_2": list(pos2_xy) + [z2],
                },
            }

            await asyncio.sleep(0.5)

        self.running = False


@app.websocket("/ws/negotiate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = KadmonSession()

    try:
        while True:
            data = await websocket.receive_text()
            params = json.loads(data)

            session.tri.set_query_position(params.get('x', -0.75), params.get('y', 0.0), params.get('z', 0.0))

            # New payload format: agents list
            agents = params.get('agents', [])

            # Backwards compat: if old agent1_url/agent2_url keys are present and no agents list
            if not agents:
                agent1_url = params.get('agent1_url', '')
                agent2_url = params.get('agent2_url', '')
                agent1_model = params.get('agent1_model', 'agent_1')
                agent2_model = params.get('agent2_model', 'agent_2')
                agents = [
                    {"id": "agent_1", "url": agent1_url, "model": agent1_model, "name": "agent_1"},
                    {"id": "agent_2", "url": agent2_url, "model": agent2_model, "name": "agent_2"},
                ]

            session.agents = agents
            session.user_prompt = params.get('user_prompt', 'Discuss.')
            mode = params.get('mode', 'PAIR')

            # Initialise the 2nd order PAIR/COUPLE within the 1st order environment
            session.init_pair(agents, mode)

            async for frame in session.run_negotiation():
                await websocket.send_text(json.dumps(frame))

    except Exception as e:
        session.running = False
        await websocket.close()


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------

@app.get("/api/status")
def status():
    """Return full 1st order environment state."""
    plugin_snap = kadmon_env.plugin_status()
    return {
        "status": "running",
        "version": "1.0",
        "environment_id": kadmon_env.environment_id,
        "center_point": -0.500003,
        "running": kadmon_env.running,
        "systems": kadmon_env.contained_systems,
        "plugins": {
            "available": len(plugin_snap["available_plugins"]),
            "installed": len(plugin_snap["installed"]),
            "enabled": sum(1 for i in plugin_snap["installed"] if i["status"] == "enabled")
        }
    }


@app.get("/api/agents")
def get_agents():
    """Return all 3rd order LLMs registered in the 1st order environment."""
    return {
        "agents": kadmon_env.contained_systems["third_order"],
        "center_point": -0.500003
    }


# ---------------------------------------------------------------------------
# /api/memory — MCPMemoryServer operations (4th order, accessed via 1st order bridge)
# ---------------------------------------------------------------------------

class MemoryCreateRequest(BaseModel):
    context_id: str = None

class MemoryWriteRequest(BaseModel):
    context_id: str
    key: str
    value: object

@app.post("/api/memory/create")
def memory_create(req: MemoryCreateRequest = None):
    """Create a new MCP memory context. Returns the context_id."""
    context_id = req.context_id if req else None
    created_id = kadmon_env.create_memory_server(context_id)
    return {"context_id": created_id}

@app.post("/api/memory/write")
def memory_write(req: MemoryWriteRequest):
    """Write a key/value pair into the specified memory context."""
    entry_id = kadmon_env.memory_write(req.context_id, req.key, req.value)
    return {"entry_id": entry_id, "context_id": req.context_id, "key": req.key}

@app.get("/api/memory/read")
def memory_read(
    context_id: str = Query(..., description="Memory context ID"),
    key: str = Query(..., description="Key to read"),
):
    """Read a value from the specified memory context by key."""
    value = kadmon_env.memory_read(context_id, key)
    return {"context_id": context_id, "key": key, "value": value}


# ---------------------------------------------------------------------------
# /api/plugins — Kadmon modular plugin system
# ---------------------------------------------------------------------------

class PluginInstallRequest(BaseModel):
    plugin_id: str
    config: dict = {}

class PluginActionRequest(BaseModel):
    instance_id: str

@app.get("/api/plugins")
def list_plugins():
    """Return all available plugin manifests and installed instances."""
    return kadmon_env.plugin_status()

@app.get("/api/plugins/available")
def list_available_plugins():
    """Return all available plugin manifests (installable modules)."""
    available = kadmon_env.list_available_plugins()
    return {
        "plugins": [
            {
                "plugin_id": m.plugin_id,
                "name": m.name,
                "order": m.order.value,
                "version": m.version,
                "description": m.description,
                "singleton": m.singleton,
                "config_schema": m.config_schema,
                "requires": m.requires
            }
            for m in available
        ]
    }

@app.post("/api/plugins/install")
def install_plugin(req: PluginInstallRequest):
    """Install a plugin by plugin_id. Returns the created PluginInstance."""
    try:
        instance = kadmon_env.install_plugin(req.plugin_id, req.config)
        return {
            "instance_id": instance.instance_id,
            "plugin_id": instance.manifest.plugin_id,
            "name": instance.manifest.name,
            "order": instance.manifest.order.value,
            "status": instance.status.value,
            "installed_at": instance.installed_at.isoformat()
        }
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/plugins/enable")
def enable_plugin(req: PluginActionRequest):
    """Enable an installed plugin by instance_id."""
    try:
        instance = kadmon_env.enable_plugin(req.instance_id)
        return {"instance_id": instance.instance_id, "status": instance.status.value}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/plugins/disable")
def disable_plugin(req: PluginActionRequest):
    """Disable a running plugin."""
    try:
        instance = kadmon_env.disable_plugin(req.instance_id)
        return {"instance_id": instance.instance_id, "status": instance.status.value}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/plugins/{instance_id}")
def uninstall_plugin(instance_id: str):
    """Uninstall a disabled plugin."""
    try:
        kadmon_env.uninstall_plugin(instance_id)
        return {"uninstalled": instance_id}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------------------------
# /api/nych — NYCH 5th order VST plugin interface
# ---------------------------------------------------------------------------

from engine.nych import NYCHSystem as _NYCHSystem

_nych_system = _NYCHSystem()

class NychProcessRequest(BaseModel):
    text: str
    inject_header: bool = False

@app.post("/api/nych/process")
def nych_process(req: NychProcessRequest):
    """
    Process text through the NYCH 5th order system.
    Returns: symbol_stream, domain analysis, TOTE loops, stability score.
    This is the VST plugin interface entry point for NYCH inside Kadmon.
    """
    symbol_stream = _nych_system.encode_stream(req.text)
    domain = _nych_system.extract_domain(req.text)
    tokens = _nych_system.encode_text(req.text)

    header = None
    if req.inject_header:
        from engine.nych import NYCHBridge
        bridge = NYCHBridge()
        header = bridge.inject_prompt_header(req.text)

    token_list = [
        {"word": w, "emoji": e, "consonants": c}
        for (e, c), w in zip(tokens, req.text.lower().split()[:len(tokens)])
    ]

    # Compute overall stability from cache
    cache = _nych_system.gestalt_cache
    stability = (
        sum(m.stability for m in cache.values()) / max(1, len(cache))
        if cache else 0.0
    )

    return {
        "symbol_stream": symbol_stream,
        "domain": domain,
        "tokens": token_list,
        "stability": round(stability, 4),
        "order": 5,
        "header": header,
    }


@app.get("/api/nych/operators")
def nych_operators():
    """Return the NYCH operator set and invariant symbol table."""
    from engine.nych import INVARIANT_SYMBOLS
    return {
        "operators": ["align", "check", "shift", "amplify", "interrupt", "stabilize"],
        "invariant_symbols": {k: v for k, v in INVARIANT_SYMBOLS.items()},
        "order": 5,
        "description": "NYCH 5th order zero-API gestalt encoder"
    }


# ---------------------------------------------------------------------------
# /api/systems/tree — Systems tree state for flowchart UI
# ---------------------------------------------------------------------------

import copy

# Default systems tree: hierarchical nodes representing the System of Systems
_DEFAULT_SYSTEMS_TREE = {
    "nodes": [
        {
            "id": "kadmon_1st",
            "type": "system",
            "order": 1,
            "label": "KADMON RUNTIME",
            "description": "1st Order — Outermost container. Invariant center C = -0.500003",
            "color": "#00ffaa",
            "position": {"x": 400, "y": 40},
            "locked": True
        },
        {
            "id": "pair_2nd",
            "type": "system",
            "order": 2,
            "label": "PAIR / COUPLE",
            "description": "2nd Order — Dual LLM configuration sharing invariant center",
            "color": "#00aaff",
            "position": {"x": 400, "y": 160},
            "locked": False
        },
        {
            "id": "llm_gpt_3rd",
            "type": "system",
            "order": 3,
            "label": "GPT [3rd]",
            "description": "3rd Order — OpenAI GPT LLM backend",
            "color": "#00ff88",
            "position": {"x": 160, "y": 300},
            "locked": False
        },
        {
            "id": "llm_claude_3rd",
            "type": "system",
            "order": 3,
            "label": "Claude [3rd]",
            "description": "3rd Order — Anthropic Claude LLM backend",
            "color": "#00ff88",
            "position": {"x": 400, "y": 300},
            "locked": False
        },
        {
            "id": "llm_gemini_3rd",
            "type": "system",
            "order": 3,
            "label": "Gemini [3rd]",
            "description": "3rd Order — Google Gemini LLM backend",
            "color": "#00ff88",
            "position": {"x": 640, "y": 300},
            "locked": False
        },
        {
            "id": "mgate_4th",
            "type": "system",
            "order": 4,
            "label": "MGATE DAG [4th]",
            "description": "4th Order — Deterministic boolean gate DAG pipeline",
            "color": "#ffaa44",
            "position": {"x": 200, "y": 460},
            "locked": False
        },
        {
            "id": "mcp_memory_4th",
            "type": "system",
            "order": 4,
            "label": "MCP Memory [4th]",
            "description": "4th Order — Mandelbrot-anchored key-value memory server",
            "color": "#ffaa44",
            "position": {"x": 440, "y": 460},
            "locked": False
        },
        {
            "id": "mobius_4th",
            "type": "system",
            "order": 4,
            "label": "Möbius TMT [4th]",
            "description": "4th Order — Triadic Möbius holonomy transport",
            "color": "#ffaa44",
            "position": {"x": 680, "y": 460},
            "locked": False
        },
        {
            "id": "nych_5th",
            "type": "system",
            "order": 5,
            "label": "NYCH [5th]",
            "description": "5th Order — Zero-API gestalt emoji encoder. Insertable at any level.",
            "color": "#cc88ff",
            "position": {"x": 400, "y": 620},
            "locked": False
        }
    ],
    "edges": [
        {"id": "e1", "source": "kadmon_1st", "target": "pair_2nd"},
        {"id": "e2", "source": "pair_2nd", "target": "llm_gpt_3rd"},
        {"id": "e3", "source": "pair_2nd", "target": "llm_claude_3rd"},
        {"id": "e4", "source": "pair_2nd", "target": "llm_gemini_3rd"},
        {"id": "e5", "source": "llm_gpt_3rd", "target": "mgate_4th"},
        {"id": "e6", "source": "llm_claude_3rd", "target": "mcp_memory_4th"},
        {"id": "e7", "source": "llm_gemini_3rd", "target": "mobius_4th"},
        {"id": "e8", "source": "mgate_4th", "target": "nych_5th"},
        {"id": "e9", "source": "mcp_memory_4th", "target": "nych_5th"},
        {"id": "e10", "source": "mobius_4th", "target": "nych_5th"},
    ]
}

# Mutable in-memory tree state (per server session)
_systems_tree_state = copy.deepcopy(_DEFAULT_SYSTEMS_TREE)


class SystemsTreeNode(BaseModel):
    id: str
    type: str = "system"
    order: int
    label: str
    description: str = ""
    color: str = "#778899"
    position: dict = {}
    locked: bool = False

class SystemsTreeEdge(BaseModel):
    id: str
    source: str
    target: str

class SystemsTreeState(BaseModel):
    nodes: list
    edges: list


@app.get("/api/systems/tree")
def get_systems_tree():
    """Return the current systems tree state (nodes + edges) for the flowchart UI."""
    return _systems_tree_state


@app.post("/api/systems/tree")
def update_systems_tree(state: SystemsTreeState):
    """
    Replace the systems tree state.
    The frontend flowchart sends node positions (after drag) and edge changes here.
    """
    global _systems_tree_state
    _systems_tree_state = {"nodes": state.nodes, "edges": state.edges}
    return {"ok": True, "node_count": len(state.nodes), "edge_count": len(state.edges)}


@app.post("/api/systems/tree/node")
def add_tree_node(node: SystemsTreeNode):
    """Add a new system node to the tree."""
    global _systems_tree_state
    # Remove existing node with same id if present
    _systems_tree_state["nodes"] = [n for n in _systems_tree_state["nodes"] if n["id"] != node.id]
    _systems_tree_state["nodes"].append({
        "id": node.id,
        "type": node.type,
        "order": node.order,
        "label": node.label,
        "description": node.description,
        "color": node.color,
        "position": node.position,
        "locked": node.locked
    })
    return {"ok": True, "id": node.id}


@app.delete("/api/systems/tree/node/{node_id}")
def delete_tree_node(node_id: str):
    """Remove a system node and all its edges from the tree."""
    global _systems_tree_state
    # Check locked
    node = next((n for n in _systems_tree_state["nodes"] if n["id"] == node_id), None)
    if node and node.get("locked"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Node '{node_id}' is locked (1st order) and cannot be removed.")
    _systems_tree_state["nodes"] = [n for n in _systems_tree_state["nodes"] if n["id"] != node_id]
    _systems_tree_state["edges"] = [
        e for e in _systems_tree_state["edges"]
        if e["source"] != node_id and e["target"] != node_id
    ]
    return {"ok": True, "deleted": node_id}


@app.post("/api/systems/tree/reset")
def reset_systems_tree():
    """Reset the systems tree to the default hierarchy."""
    global _systems_tree_state
    _systems_tree_state = copy.deepcopy(_DEFAULT_SYSTEMS_TREE)
    return {"ok": True, "message": "Systems tree reset to default hierarchy"}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
