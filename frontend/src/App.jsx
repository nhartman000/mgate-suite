import React, { useState, useEffect, useRef } from 'react'
import Scene3D from './Scene3D'
import NychPanel from './NychPanel'
import SystemsTree from './SystemsTree'

const MODEL_TYPES = ["GPT", "Grok", "Gemini", "Claude", "Custom"]
const CENTER_POINT = [-0.500003, 0.0, 0.0]

const KADMON_POINTS_REF = [
  { name: "container",         x: -0.750000, y:  0.000000, role: "IU start" },
  { name: "triangle_upper",    x: -0.750000, y:  0.125000, role: "Agent 1 anchor" },
  { name: "triangle_lower",    x: -0.750000, y: -0.125000, role: "Agent 2 anchor" },
  { name: "bulb_upper_center", x: -0.875000, y:  0.216500, role: "Upper bulb" },
  { name: "bulb_lower_center", x: -0.875000, y: -0.216500, role: "Lower bulb" },
  { name: "stability_anchor",  x: -0.500003, y:  0.000000, role: "C — invariant center" },
  { name: "user_anchor",       x: -1.310000, y:  0.000000, role: "USER (period-4 bulb)" },
]

const AGENT_COLORS = [
  { emoji: '🔵', color: '#00aaff', border: '#00aaff', bg: '#003377', selectColor: '#aaddff' },
  { emoji: '🟢', color: '#00ff88', border: '#00ff88', bg: '#004422', selectColor: '#aaffdd' },
  { emoji: '🟣', color: '#cc88ff', border: '#cc88ff', bg: '#220055', selectColor: '#ddaaff' },
  { emoji: '🟠', color: '#ff9944', border: '#ff9944', bg: '#441100', selectColor: '#ffcc99' },
  { emoji: '🔴', color: '#ff4455', border: '#ff4455', bg: '#440011', selectColor: '#ffaaaa' },
]

const ORDER_COLORS = {
  2: '#00aaff',
  3: '#00ff88',
  4: '#ffaa44',
  5: '#cc88ff',
}

function makeAgent(index) {
  return {
    id: typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : String(Date.now() + index),
    name: `agent_${index + 1}`,
    model: "GPT",
    endpoint: "",
    registered: false,
    status: "offline",
    lastResponse: ""
  }
}

function fmtCoord(v) {
  const s = v >= 0 ? '+' : ''
  return `${s}${v.toFixed(6)}`
}

export default function App() {
  const [agents, setAgents] = useState([makeAgent(0), makeAgent(1)])
  const [prompts, setPrompts] = useState({})
  const [negotiationLog, setNegotiationLog] = useState([])
  const [trainingActive, setTrainingActive] = useState(false)
  const [round, setRound] = useState(0)
  const [status, setStatus] = useState("System Ready")
  const [negotiationMode, setNegotiationMode] = useState("PAIR")
  const [negotiationPositions, setNegotiationPositions] = useState({})

  const [coords, setCoords] = useState({
    user: [-1.31, 0, 0],
    query: [-0.75, 0, 0],
    ai: [-0.5, 0, 0],
    iu: [-0.75, 0, 0],
    center: CENTER_POINT
  })
  const [ws, setWs] = useState(null)

  // Plugin Manager state
  const [plugins, setPlugins] = useState({ available_plugins: [], installed: [] })
  const [pluginsOpen, setPluginsOpen] = useState(false)
  const [nychResult, setNychResult] = useState(null)

  useEffect(() => {
    return () => {
      if (ws) ws.close()
    }
  }, [ws])

  useEffect(() => {
    fetch('/api/plugins')
      .then(r => r.json())
      .then(data => setPlugins(data))
      .catch(() => {})
  }, [])

  const addAgent = () => {
    const idx = agents.length
    const newAgent = makeAgent(idx)
    setAgents(prev => [...prev, newAgent])
    setNegotiationLog(prev => [...prev, `➕ Agent slot ${idx + 1} created`])
  }

  const updateAgent = (id, patch) => {
    setAgents(prev => prev.map(a => a.id === id ? { ...a, ...patch } : a))
  }

  const registerAgent = (agent, index) => {
    updateAgent(agent.id, { registered: true, status: "connected" })
    setNegotiationLog(prev => [...prev, `✅ Agent ${index + 1} registered: ${agent.name} [${agent.model}]`])
  }

  const registeredAgents = agents.filter(a => a.registered)

  const startNegotiation = () => {
    if (registeredAgents.length < 2) {
      setStatus("At least 2 agents must be registered")
      return
    }
    setTrainingActive(true)
    setRound(1)
    setNegotiationLog(prev => [...prev, `🚀 Triadic negotiation loop initiated [MODE: ${negotiationMode}] [AGENTS: ${registeredAgents.length}]`])
    setStatus("Training Active")

    const userPrompt = registeredAgents
      .map((a, i) => `A${i + 1}:[${prompts[a.id] || ''}]`)
      .join(' ')

    const socket = new WebSocket('ws://127.0.0.1:8000/ws/negotiate')
    socket.onopen = () => {
      console.log('Connected to WebSocket')
      socket.send(JSON.stringify({
        x: -0.75,
        y: 0.0,
        z: 0.0,
        agents: registeredAgents.map((a, i) => ({
          id: `agent_${i + 1}`,
          url: a.endpoint,
          model: a.model,
          name: a.name
        })),
        user_prompt: userPrompt,
        mode: negotiationMode
      }))
    }
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)

      setCoords({
        user: data.user,
        query: data.query,
        ai: data.ai,
        iu: data.iu || [-0.75, 0, 0],
        center: data.center || CENTER_POINT
      })

      // agent_responses is { agent_1: "...", agent_2: "...", ... }
      if (data.agent_responses && typeof data.agent_responses === 'object') {
        setAgents(prev => prev.map((a, i) => {
          const key = `agent_${i + 1}`
          const resp = data.agent_responses[key]
          return resp !== undefined ? { ...a, lastResponse: resp } : a
        }))
      }

      // negotiation_positions: { agent_1: [x,y,z], agent_2: [x,y,z] }
      if (data.negotiation_positions) {
        setNegotiationPositions(data.negotiation_positions)
      }

      setRound(data.round)
      if (typeof data.alignment_gap === 'number' && data.round % 5 === 0) {
        setNegotiationLog(prev => [...prev,
          `〽️ Round ${data.round} — Gap: ${data.alignment_gap.toFixed(4)} Stability: ${data.stability.toFixed(4)} Mode: ${data.mode}`
        ])
      }
    }
    socket.onclose = () => {
      setTrainingActive(false)
      setStatus("Negotiation completed or disconnected")
    }
    setWs(socket)
  }

  const sendPromptForAgent = async (agent, index) => {
    const promptText = prompts[agent.id] || ''
    if (!promptText.trim()) return

    let hash = 0
    for (let i = 0; i < promptText.length; i++) {
      hash = promptText.charCodeAt(i) + ((hash << 5) - hash)
    }
    const h1 = Math.abs((hash % 1000) / 1000.0)
    const h2 = ((hash >> 4) % 1000) / 1000.0
    const h3 = ((hash >> 8) % 1000) / 1000.0
    const agentMult = index % 2 === 0 ? -1 : 1
    const newQuery = [-0.75 + (h1 * 0.5), h2 * 0.5 * agentMult, h3 * 0.5]

    setCoords(prev => ({ ...prev, query: newQuery }))
    setNegotiationLog(prev => [...prev, `📤 Agent ${index + 1} Input Logged: ${promptText}`])
    updateAgent(agent.id, { lastResponse: "Fetching formulation..." })

    try {
      const response = await fetch("http://127.0.0.1:8000/api/prompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: agent.endpoint, prompt: promptText })
      })
      const data = await response.json()
      updateAgent(agent.id, { lastResponse: data.response })
    } catch (e) {
      updateAgent(agent.id, { lastResponse: `[NETWORK ERROR] ${e.message}` })
    }
  }

  const installPlugin = async (plugin_id) => {
    const res = await fetch('/api/plugins/install', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plugin_id, config: {} })
    })
    const data = await res.json()
    const updated = await fetch('/api/plugins').then(r => r.json())
    setPlugins(updated)
    setNegotiationLog(prev => [...prev, `🔌 Plugin installed: ${plugin_id} [${data.instance_id?.slice(0, 8)}]`])
  }

  const enablePlugin = async (instance_id) => {
    await fetch('/api/plugins/enable', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ instance_id })
    })
    const updated = await fetch('/api/plugins').then(r => r.json())
    setPlugins(updated)
    setNegotiationLog(prev => [...prev, `✅ Plugin enabled: ${instance_id.slice(0, 8)}`])
  }

  const disablePlugin = async (instance_id) => {
    await fetch('/api/plugins/disable', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ instance_id })
    })
    const updated = await fetch('/api/plugins').then(r => r.json())
    setPlugins(updated)
  }

  const iuFmt = coords.iu.map(v => v.toFixed(4)).join(", ")

  const installedIds = new Set((plugins.installed || []).map(p => p.plugin_id))

  // Group available plugins by order
  const availableByOrder = {}
  for (const p of (plugins.available_plugins || [])) {
    const ord = p.order ?? 2
    if (!availableByOrder[ord]) availableByOrder[ord] = []
    availableByOrder[ord].push(p)
  }
  const orderLabels = { 2: '2nd', 3: '3rd', 4: '4th', 5: '5th' }

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0a0a1a',
      color: '#e0e0e0',
      display: 'flex',
      flexDirection: 'row',
      fontFamily: 'system-ui'
    }}>

      {/* LEFT DASHBOARD PANEL */}
      <div style={{ flex: 1, padding: 20, display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
        <h1 style={{ color: '#00ffaa', margin: '0 0 4px 0', borderBottom: '1px solid #223', paddingBottom: 8, fontFamily: 'monospace', letterSpacing: 2 }}>
          1st ORDER KADMON RUNTIME ENVIRONMENT
        </h1>

        {/* SYSTEM HIERARCHY PANEL */}
        <div style={{
          background: '#0c0c22',
          border: '1px solid #334466',
          borderRadius: 6,
          padding: '10px 14px',
          marginBottom: 12,
          fontFamily: 'monospace',
          fontSize: 12,
          color: '#99bbdd',
          lineHeight: 1.8
        }}>
          <div style={{ color: '#00ffaa', fontWeight: 'bold', marginBottom: 4, letterSpacing: 1 }}>◈ KADMON SYSTEM HIERARCHY</div>
          <div><span style={{ color: '#556677' }}>1st Order:</span> <span style={{ color: '#00ffaa' }}>KADMON RUNTIME</span></div>
          <div>
            <span style={{ color: '#556677' }}>2nd Order:</span>{' '}
            <span style={{ color: negotiationMode === 'COUPLE' ? '#ff88ff' : '#00aaff' }}>{negotiationMode}</span>
            {' '}<span style={{ color: '#556677' }}>— Shared C =</span>{' '}
            <span style={{ color: '#ffdd00' }}>-0.500003</span>
          </div>
          <div>
            <span style={{ color: '#556677' }}>3rd Order:</span>{' '}
            {agents.map((a, i) => {
              const c = AGENT_COLORS[i % AGENT_COLORS.length]
              return (
                <span key={a.id}>
                  <span style={{ color: c.color }}>[{a.model}] {a.name}</span>
                  {i < agents.length - 1 && <span style={{ color: '#445' }}> + </span>}
                </span>
              )
            })}
          </div>
          <div>
            <span style={{ color: '#556677' }}>IU Position:</span>{' '}
            <span style={{ color: '#ffaa44' }}>[{iuFmt}]</span>
          </div>
        </div>

        {/* MANDELBROT NEGOTIATION GEOMETRY PANEL */}
        <div style={{
          background: '#07071a',
          border: '1px solid #2a3a55',
          borderRadius: 6,
          padding: '10px 14px',
          marginBottom: 16,
          fontFamily: 'monospace',
          fontSize: 11,
          color: '#8899bb',
          lineHeight: 2.0
        }}>
          <div style={{ color: '#00ccff', fontWeight: 'bold', marginBottom: 6, letterSpacing: 1, fontSize: 12 }}>◈ MANDELBROT NEGOTIATION GEOMETRY</div>
          {KADMON_POINTS_REF.map(pt => {
            const isAnchor = pt.name === 'stability_anchor'
            const ySign = pt.y >= 0 ? '+' : ''
            return (
              <div key={pt.name} style={{
                display: 'flex',
                gap: 8,
                background: isAnchor ? 'rgba(255,220,0,0.08)' : 'transparent',
                borderRadius: isAnchor ? 3 : 0,
                padding: isAnchor ? '0 4px' : 0,
              }}>
                <span style={{ color: isAnchor ? '#ffdd00' : '#446688', minWidth: 20 }}>{isAnchor ? '►' : ' '}</span>
                <span style={{ color: isAnchor ? '#ffdd00' : '#5577aa', minWidth: 200 }}>{pt.name}</span>
                <span style={{ color: isAnchor ? '#ffe066' : '#334466', minWidth: 8 }}>:</span>
                <span style={{ color: isAnchor ? '#ffe066' : '#7799cc', minWidth: 220 }}>
                  ({pt.x.toFixed(6)}, {ySign}{pt.y.toFixed(6)})
                </span>
                <span style={{ color: isAnchor ? '#ffbb00' : '#445566' }}>← {pt.role}</span>
              </div>
            )
          })}
        </div>

        {/* PLUGIN MANAGER PANEL */}
        <div style={{
          background: '#0a0a1a',
          border: '1px solid #2a2a44',
          borderRadius: 6,
          marginBottom: 16,
          fontFamily: 'monospace',
          fontSize: 12,
          overflow: 'hidden'
        }}>
          {/* Header toggle button */}
          <button
            onClick={() => setPluginsOpen(o => !o)}
            style={{
              width: '100%',
              padding: '10px 14px',
              background: '#0c0c22',
              border: 'none',
              borderBottom: pluginsOpen ? '1px solid #2a2a44' : 'none',
              color: '#aabbdd',
              fontFamily: 'monospace',
              fontSize: 12,
              fontWeight: 'bold',
              letterSpacing: 1,
              cursor: 'pointer',
              textAlign: 'left',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <span>🔌 PLUGIN MANAGER ({(plugins.installed || []).length} installed)</span>
            <span style={{ color: '#556677', fontSize: 10 }}>{pluginsOpen ? '▲ COLLAPSE' : '▼ EXPAND'}</span>
          </button>

          {pluginsOpen && (
            <div style={{ padding: '12px 14px' }}>

              {/* INSTALLED section */}
              {(plugins.installed || []).length > 0 && (
                <div style={{ marginBottom: 14 }}>
                  <div style={{ color: '#778899', fontSize: 11, letterSpacing: 1, marginBottom: 6, borderBottom: '1px solid #1a2a3a', paddingBottom: 4 }}>
                    INSTALLED
                  </div>
                  {(plugins.installed || []).map(p => {
                    const isEnabled = p.status === 'enabled' || p.enabled === true
                    return (
                      <div key={p.instance_id} style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 8,
                        padding: '5px 0',
                        borderBottom: '1px solid #111822'
                      }}>
                        <span style={{ color: isEnabled ? '#00ff88' : '#445566', fontSize: 14 }}>
                          {isEnabled ? '●' : '○'}
                        </span>
                        <span style={{ color: '#ccddf0', flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {p.plugin_id || p.name || p.instance_id?.slice(0, 12)}
                        </span>
                        {p.order != null && (
                          <span style={{ color: ORDER_COLORS[p.order] ?? '#778899', fontSize: 10 }}>
                            order:{p.order}
                          </span>
                        )}
                        {p.version && (
                          <span style={{ color: '#445566', fontSize: 10 }}>{p.version}</span>
                        )}
                        <span style={{
                          padding: '1px 6px',
                          borderRadius: 3,
                          fontSize: 10,
                          background: isEnabled ? '#003322' : '#1a1a2e',
                          color: isEnabled ? '#00ff88' : '#556677',
                          border: `1px solid ${isEnabled ? '#00aa44' : '#334'}`,
                          whiteSpace: 'nowrap'
                        }}>
                          {p.status ?? (isEnabled ? 'enabled' : 'disabled')}
                        </span>
                        {isEnabled ? (
                          <button
                            onClick={() => disablePlugin(p.instance_id)}
                            style={{
                              padding: '2px 8px',
                              background: '#220011',
                              border: '1px solid #550033',
                              color: '#ff6677',
                              fontFamily: 'monospace',
                              fontSize: 10,
                              cursor: 'pointer',
                              borderRadius: 3,
                              whiteSpace: 'nowrap'
                            }}
                          >
                            DISABLE
                          </button>
                        ) : (
                          <button
                            onClick={() => enablePlugin(p.instance_id)}
                            style={{
                              padding: '2px 8px',
                              background: '#002211',
                              border: '1px solid #005533',
                              color: '#00ff88',
                              fontFamily: 'monospace',
                              fontSize: 10,
                              cursor: 'pointer',
                              borderRadius: 3,
                              whiteSpace: 'nowrap'
                            }}
                          >
                            ENABLE
                          </button>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}

              {/* AVAILABLE TO INSTALL section */}
              {(plugins.available_plugins || []).length > 0 && (
                <div>
                  <div style={{ color: '#778899', fontSize: 11, letterSpacing: 1, marginBottom: 6, borderBottom: '1px solid #1a2a3a', paddingBottom: 4 }}>
                    AVAILABLE TO INSTALL
                  </div>
                  {Object.keys(availableByOrder).sort((a, b) => Number(a) - Number(b)).map(ord => {
                    const ordNum = Number(ord)
                    const ordColor = ORDER_COLORS[ordNum] ?? '#778899'
                    const label = orderLabels[ordNum] ?? `${ord}th`
                    return (
                      <div key={ord} style={{ marginBottom: 10 }}>
                        <div style={{ color: ordColor, fontSize: 10, letterSpacing: 1, marginBottom: 4, opacity: 0.8 }}>
                          ── {label} ORDER ──
                        </div>
                        {availableByOrder[ord].map(p => {
                          const alreadyInstalled = installedIds.has(p.plugin_id)
                          return (
                            <div key={p.plugin_id} style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: 8,
                              padding: '4px 0',
                              borderBottom: '1px solid #0f1522'
                            }}>
                              <span style={{ color: ordColor, fontWeight: 'bold', fontSize: 11, minWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                {p.plugin_id}
                              </span>
                              <span style={{ color: '#556677', flex: 1, fontSize: 10, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                — {p.description ?? ''}
                              </span>
                              {alreadyInstalled ? (
                                <span style={{ color: '#445566', fontSize: 10, whiteSpace: 'nowrap' }}>installed</span>
                              ) : (
                                <button
                                  onClick={() => installPlugin(p.plugin_id)}
                                  style={{
                                    padding: '2px 8px',
                                    background: '#0a1a2a',
                                    border: `1px solid ${ordColor}55`,
                                    color: ordColor,
                                    fontFamily: 'monospace',
                                    fontSize: 10,
                                    cursor: 'pointer',
                                    borderRadius: 3,
                                    whiteSpace: 'nowrap'
                                  }}
                                >
                                  INSTALL
                                </button>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    )
                  })}
                </div>
              )}

              {(plugins.available_plugins || []).length === 0 && (plugins.installed || []).length === 0 && (
                <div style={{ color: '#334455', fontStyle: 'italic', fontSize: 11 }}>No plugins available</div>
              )}
            </div>
          )}
        </div>

        {/* NYCH VST PLUGIN PANEL */}
        <NychPanel onNychResult={setNychResult} />

        {/* SYSTEMS TREE — ORDER HIERARCHY FLOWCHART */}
        <SystemsTree installedPlugins={plugins.installed} />

        {/* ADD AGENT BUTTON */}
        <button
          onClick={addAgent}
          style={{
            display: 'block',
            width: '100%',
            padding: '12px 0',
            marginBottom: 16,
            background: 'transparent',
            border: '2px dashed #334466',
            borderRadius: 8,
            color: '#5577aa',
            fontFamily: 'monospace',
            fontSize: 14,
            fontWeight: 'bold',
            letterSpacing: 2,
            cursor: 'pointer',
            textAlign: 'center',
            transition: 'border-color 0.2s, color 0.2s'
          }}
          onMouseEnter={e => { e.target.style.borderColor = '#00aaff'; e.target.style.color = '#00aaff' }}
          onMouseLeave={e => { e.target.style.borderColor = '#334466'; e.target.style.color = '#5577aa' }}
        >
          + ADD AGENT
        </button>

        {/* AGENT GRID */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 0 }}>
          {agents.map((agent, index) => {
            const scheme = AGENT_COLORS[index % AGENT_COLORS.length]
            const prompt = prompts[agent.id] || ''
            return (
              <div key={agent.id} style={{
                background: '#112',
                padding: 16,
                borderRadius: 8,
                border: agent.registered ? `2px solid ${scheme.border}` : '1px solid #223'
              }}>
                <h3 style={{ color: scheme.color, marginTop: 0, fontFamily: 'monospace', letterSpacing: 1 }}>
                  {scheme.emoji} AGENT {index + 1}
                </h3>

                <input
                  placeholder="Agent Name"
                  value={agent.name}
                  onChange={e => updateAgent(agent.id, { name: e.target.value })}
                  style={{
                    width: '100%', margin: '8px 0', padding: 8,
                    background: '#001', border: '1px solid #224', color: '#fff',
                    boxSizing: 'border-box', fontFamily: 'monospace'
                  }}
                />

                <select
                  value={agent.model}
                  onChange={e => updateAgent(agent.id, { model: e.target.value })}
                  style={{
                    width: '100%', margin: '0 0 8px 0', padding: 8,
                    background: '#001', border: '1px solid #224', color: scheme.selectColor,
                    boxSizing: 'border-box', fontFamily: 'monospace'
                  }}
                >
                  {MODEL_TYPES.map(m => <option key={m} value={m}>{m}</option>)}
                </select>

                <input
                  placeholder="API Endpoint"
                  value={agent.endpoint}
                  onChange={e => updateAgent(agent.id, { endpoint: e.target.value })}
                  style={{
                    width: '100%', margin: '0 0 8px 0', padding: 8,
                    background: '#001', border: '1px solid #224', color: '#fff',
                    boxSizing: 'border-box', fontFamily: 'monospace', fontSize: 11
                  }}
                />

                <button
                  onClick={() => registerAgent(agent, index)}
                  disabled={agent.registered}
                  style={{
                    width: '100%', padding: 10,
                    background: agent.registered ? '#004422' : scheme.bg,
                    border: agent.registered ? `1px solid ${scheme.border}` : '1px solid #335',
                    color: agent.registered ? '#00ff88' : '#fff',
                    cursor: agent.registered ? 'default' : 'pointer',
                    boxSizing: 'border-box', marginBottom: 10,
                    fontFamily: 'monospace', fontWeight: 'bold', letterSpacing: 1
                  }}
                >
                  {agent.registered ? `✓ REGISTERED` : `REGISTER AGENT ${index + 1}`}
                </button>

                <input
                  placeholder={`Agent ${index + 1} Semantic Prompt...`}
                  value={prompt}
                  onChange={e => setPrompts(prev => ({ ...prev, [agent.id]: e.target.value }))}
                  style={{
                    width: '100%', padding: 8,
                    background: '#001', border: '1px solid #224', color: '#fff',
                    boxSizing: 'border-box', marginBottom: 5, fontFamily: 'monospace', fontSize: 11
                  }}
                />

                <button
                  onClick={() => sendPromptForAgent(agent, index)}
                  style={{
                    width: '100%', padding: 8,
                    background: '#ff8800', border: 'none', color: '#000',
                    cursor: 'pointer', fontWeight: 'bold', fontFamily: 'monospace', letterSpacing: 1
                  }}
                >
                  SEND TO A{index + 1}
                </button>

                <div style={{ marginTop: 10, fontSize: 12, color: '#88a', fontFamily: 'monospace' }}>
                  Status: <span style={{ color: agent.registered ? '#00ff88' : '#556677' }}>{agent.status}</span>
                  {' '}| Model: <span style={{ color: scheme.color }}>{agent.model}</span>
                </div>

                <div style={{
                  marginTop: 8, padding: 8, background: '#000', borderRadius: 4,
                  height: 80, overflowY: 'auto', fontSize: 11, color: '#aaa',
                  border: '1px solid #334', fontFamily: 'monospace'
                }}>
                  {agent.lastResponse || "Awaiting LLM response feed..."}
                </div>
              </div>
            )
          })}
        </div>

        {/* CONTROL BAR */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 20,
          margin: '20px 0',
          background: '#112',
          padding: 16,
          borderRadius: 8
        }}>
          {/* PAIR / COUPLE MODE TOGGLE */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, fontFamily: 'monospace' }}>
            <span style={{ color: '#556677', letterSpacing: 1 }}>MODE:</span>
            {["PAIR", "COUPLE"].map(mode => (
              <button
                key={mode}
                onClick={() => setNegotiationMode(mode)}
                style={{
                  padding: '7px 18px',
                  background: negotiationMode === mode
                    ? (mode === 'COUPLE' ? '#550077' : '#003377')
                    : '#1a1a2e',
                  border: negotiationMode === mode
                    ? (mode === 'COUPLE' ? '1px solid #ff88ff' : '1px solid #00aaff')
                    : '1px solid #334',
                  color: negotiationMode === mode
                    ? (mode === 'COUPLE' ? '#ff88ff' : '#00aaff')
                    : '#556',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  letterSpacing: 1,
                  borderRadius: 4,
                  fontFamily: 'monospace'
                }}
              >
                {mode}
              </button>
            ))}
          </div>

          <button
            onClick={startNegotiation}
            disabled={registeredAgents.length < 2 || trainingActive}
            style={{
              padding: '16px 48px',
              background: trainingActive ? '#224422' : (registeredAgents.length < 2 ? '#1a1a2e' : '#00cc77'),
              border: 'none',
              color: registeredAgents.length < 2 && !trainingActive ? '#445' : '#fff',
              fontSize: 16,
              letterSpacing: 1,
              fontWeight: 'bold',
              cursor: registeredAgents.length < 2 || trainingActive ? 'default' : 'pointer',
              fontFamily: 'monospace'
            }}
          >
            {trainingActive ? "🔄 COMPUTING NEGOTIATION LOOP" : "START TRIADIC NEGOTIATION"}
          </button>
        </div>

        {/* STATUS BAR */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          background: '#112',
          padding: '12px 16px',
          borderRadius: 8,
          marginBottom: 16,
          fontFamily: 'monospace',
          fontSize: 13
        }}>
          <div>ROUND: <span style={{ color: '#00ffaa' }}>{round}</span></div>
          <div>STATUS: <span style={{ color: trainingActive ? '#00ff88' : '#556677' }}>{status}</span></div>
          <div>MODE: <span style={{ color: negotiationMode === 'COUPLE' ? '#ff88ff' : '#00aaff' }}>{negotiationMode}</span></div>
          <div>C = <span style={{ color: '#ffdd00' }}>-0.500003</span></div>
          <div>IU: <span style={{ color: '#ffaa44' }}>[{iuFmt}]</span></div>
          <div>AGENTS: <span style={{ color: registeredAgents.length >= 2 ? '#00ff88' : '#ff6655' }}>{registeredAgents.length}</span> / {agents.length}</div>
        </div>

        {/* NEGOTIATION LOG */}
        <div style={{ background: '#000', padding: 16, borderRadius: 8, flex: 1, overflowY: 'auto', minHeight: 120 }}>
          <h4 style={{ marginTop: 0, color: '#ffaa00', fontFamily: 'monospace', letterSpacing: 1 }}>📋 NEGOTIATION LOG</h4>
          {negotiationLog.map((entry, i) => (
            <div key={i} style={{
              padding: '4px 0',
              borderBottom: '1px solid #111',
              fontFamily: 'monospace',
              fontSize: 13
            }}>
              {entry}
            </div>
          ))}
          {negotiationLog.length === 0 && (
            <div style={{ color: '#446', fontStyle: 'italic', fontFamily: 'monospace' }}>
              Register at least 2 agents and start negotiation to begin
            </div>
          )}
        </div>
      </div>

      {/* RIGHT 3D CANVAS PANEL */}
      <div style={{ flex: 1, borderLeft: '2px solid #223', position: 'relative' }}>
        <Scene3D
          user={coords.user}
          query={coords.query}
          ai={coords.ai}
          iu={coords.iu}
          center={coords.center}
          negotiationPositions={negotiationPositions}
        />
      </div>

    </div>
  )
}
