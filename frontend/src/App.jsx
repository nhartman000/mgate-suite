import React, { useState, useEffect, useRef } from 'react'

export default function App() {
  const [systemState = useState({
    agent1: { registered: false, name: "", endpoint: "", temperature: 0.7, status: "offline", lastResponse: "" },
    agent2: { registered: false, name: "", endpoint: "", temperature: 0.7, status: "offline", lastResponse: "" },
    agent3: { registered: false, name: "", endpoint: "", temperature: 0.7, status: "offline", lastResponse: "" }
  })
  const agents = systemState[0]
  const setAgents = systemState[1]
  
  const [prompt, setPrompt] = useState("")
  const [events, setEvents] = useState([])
  const [trainingActive, setTrainingActive] = useState(false)
  const [round, setRound] = useState(0)
  const [systemStatus, setSystemStatus] = useState("System Ready")
  const [stability, setStability] = useState(0.0)
  const [selectedAgentPrompts, setAgentPrompts] = useState({ agent1: "", agent2: "", agent3: "" })
  const [lock = useRef(null)

  const registerAgent = (agentNum) => {
    const agent = agents[`agent${agentNum}`]
    setAgents(prev => ({
      ...prev,
      [`agent${agentNum}`]: { ...agent, registered: true, status: "connected" }
    }))
    addEvent(`✅ Agent ${agentNum} registered: ${agent.name}`, 'system')
  }

  const addEvent = (text, type = 'log') => {
    setEvents(prev => [...prev, {
      id: Date.now(),
      text,
      type,
      timestamp: new Date().toLocaleTimeString(),
      round
    }])
  }

  const startNegotiation = () => {
    const connected = Object.values(agents).filter(a => a.registered).length
    if (connected < 2) {
      setSystemStatus("Minimum 2 agents required")
      return
    }
    setTrainingActive(true)
    setRound(1)
    addEvent("🚀 Triadic Mobius negotiation loop initiated", 'system')
    setSystemStatus("Negotiation Active")
    setStability(0.33)
  }

  const sendPrompt = () => {
    if (!prompt.trim()) return
    addEvent(`📤 USER PROMPT: ${prompt}`, 'input')
    
    setTimeout(() => {
      setAgentPrompts(p => ({ ...p, agent1: `Processing: ${prompt}` }))
      addEvent(`🔵 Agent 1: Evaluating prompt`, 'agent1')
    }, 300)
    
    setTimeout(() => {
      setAgentPrompts(p => ({ ...p, agent2: `Analyzing response from Agent 1` }))
      addEvent(`🟢 Agent 2: Received Agent 1 output`, 'agent2')
      setStability(s => Math.min(1.0, s + 0.08))
    }, 900)
    
    setTimeout(() => {
      if (agents.agent3.registered) {
        setAgentPrompts(p => ({ ...p, agent3: `Verifying consistency` }))
        addEvent(`🔴 Agent 3: Triangulating agreement`, 'agent3')
      }
      setRound(r => r + 1)
      setStability(s => Math.min(1.0, s + 0.05))
    }, 1600)
    
    setPrompt("")
  }

  const overrideAgent = (agentNum) => {
    addEvent(`⌨️ Manual override for Agent ${agentNum}`, 'override')
  }

  const stepRound = () => {
    setRound(r => r + 1)
    addEvent(`⏭️ Round ${round + 1} started`, 'system')
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: '#050510', 
      color: '#e0e6ff',
      padding: 12,
      fontFamily: 'Consolas, monospace',
      fontSize: 13
    }}>
      {/* SYSTEM HEADER */}
      <div style={{ 
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottom: '1px solid #1a1a3a',
        paddingBottom: 10,
        marginBottom: 12
      }}>
        <div>
          <h1 style={{ color: '#00ffaa', margin: 0, fontSize: 22 }}>KADMON 1st ORDER SYSTEM</h1>
          <div style={{ color: '#667', fontSize: 11 }}>MÖBIUS TRIADIC NEGOTIATION ENGINE v1.0</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ color: stability > 0.7 ? '#0f7 : stability > 0.4 ? '#fa0' : '#f44' }}>
            STABILITY: {(stability * 100).toFixed(1)}%
          </div>
          <div style={{ color: '#667 }}>ROUND: {round}</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr 320px', gap: 12 }}>
        
        {/* LEFT PANEL - AGENT 1 */}
        <div style={{ 
          background: '#0a0a1a', 
          padding: 12, 
          borderRadius: 4,
          border: agents.agent1.registered ? '1px solid #0088ff' : '1px solid #1a1a3a'
        }}>
          <div style={{ color: '#0088ff', fontWeight: 'bold', marginBottom: 10 }}>🔵 AGENT 1</div>
          
          <input placeholder="Name" value={agents.agent1.name}
            onChange={e => setAgents(p => ({...p, agent1: {...p.agent1, name: e.target.value}}))}
            style={{ width: '100%', margin: '4px 0', padding: 6, background: '#050510', border: '1px solid #1a1a3a', color: '#fff', fontSize: 12 }}
          />
          <input placeholder="Endpoint" value={agents.agent1.endpoint}
            onChange={e => setAgents(p => ({...p, agent1: {...p.agent1, endpoint: e.target.value}}))}
            style={{ width: '100%', margin: '4px 0', padding: 6, background: '#050510', border: '1px solid #1a1a3a', color: '#fff', fontSize: 12 }}
          />
          
          <div style={{ margin: '8px 0' }}>
            <label style={{ fontSize: 11, color: '#668' }}>Temperature: {agents.agent1.temperature}</label>
            <input type="range" min="0" max="100" value={agents.agent1.temperature * 100}
              onChange={e => setAgents(p => ({...p, agent1: {...p.agent1, temperature: e.target.value / 100}}))}
              style={{ width: '100%' }}
            />
          </div>

          <button onClick={() => registerAgent(1)} disabled={agents.agent1.registered}
            style={{ width: '100%', padding: 6, background: agents.agent1.registered ? '#003322' : '#0066cc', border: 'none', color: '#fff', fontSize: 12 }}>
            {agents.agent1.registered ? "✓ CONNECTED" : "CONNECT"}
          </button>

          <div style={{ marginTop: 10, padding: 8, background: '#050510', minHeight: 80, fontSize: 11, color: '#88a' }}>
            {selectedAgentPrompts.agent1 || "Idle"}
          </div>

          <button onClick={() => overrideAgent(1)} style={{ width: '100%', marginTop: 8, padding: 4, background: '#331100', border: 'none', color: '#fa0', fontSize: 11 }}>
            ⌨️ MANUAL OVERRIDE
          </button>
        </div>

        {/* CENTER PANEL - CONTROLS + LIVE VIEW */}
        <div>
          {/* PROMPT INPUT */}
          <div style={{ background: '#0a0a1a', padding: 12, borderRadius: 4, border: '1px solid #1a1a3a', marginBottom: 12 }}>
            <div style={{ color: '#ffaa00', marginBottom: 8 }}>📤 INPUT PROMPT</div>
            <textarea value={prompt} onChange={e => setPrompt(e.target.value)}
              placeholder="Enter prompt to inject into triadic loop..."
              onKeyDown={e => e.ctrlKey && e.key === 'Enter' && sendPrompt()}
              style={{ 
                width: '100%', height: 60, padding: 8, background: '#050510', border: '1px solid #1a1a3a', 
                color: '#fff', fontFamily: 'Consolas, fontSize: 12, resize: 'none'
              }}
            />
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <button onClick={sendPrompt} disabled={!trainingActive}
                style={{ flex: 1, padding: 8, background: '#ff8800', border: 'none', color: '#000', fontWeight: 'bold' }}>
                ▶️ SEND
              </button>
              <button onClick={startNegotiation} disabled={trainingActive}
                style={{ flex: 1, padding: 8, background: '#00aa66', border: 'none', color: '#fff', fontWeight: 'bold' }}>
                {trainingActive ? "🔄 RUNNING" : "START TRIAD"}
              </button>
              <button onClick={stepRound} style={{ padding: '0 12, background: '#224', border: 'none', color: '#fff' }}>
                ⏭️ STEP
              </button>
            </div>
          </div>

          {/* LIVE EVENT STREAM */}
          <div style={{ background: '#000', padding: 12, borderRadius: 4, border: '1px solid #112', height: 'calc(100vh - 240px)', overflowY: 'auto' }}>
            <div style={{ color: '#88f', marginBottom: 8, display: 'flex', justifyContent: 'space-between' }}>
              <span>📡 LIVE EVENT STREAM</span>
              <span style={{ color: '#666' }}>{events.length} events</span>
            </div>
            
            {events.slice().reverse().map(ev => (
              <div key={ev.id} style={{ 
                padding: '3px 0', borderBottom: '1px solid #0a0a15', fontSize: 11,
                color: ev.type === 'agent1' ? '#4af : ev.type === 'agent2' ? '#4fa' : ev.type === 'agent3' ? '#f64' : ev.type === 'input' ? '#fa0' : '#668'
              }}>
                <span style={{ color: '#445' }}>[{ev.timestamp}]</span> {ev.text}
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT PANEL - AGENT 2 */}
        <div style={{ 
          background: '#0a0a1a', 
          padding: 12, 
          borderRadius: 4,
          border: agents.agent2.registered ? '1px solid #00ff88' : '1px solid #1a1a3a'
        }}>
          <div style={{ color: '#00ff88', fontWeight: 'bold', marginBottom: 10 }}>🟢 AGENT 2</div>
          
          <input placeholder="Name" value={agents.agent2.name}
            onChange={e => setAgents(p => ({...p, agent2: {...p.agent2, name: e.target.value}}))}
            style={{ width: '100%', margin: '4px 0', padding: 6, background: '#050510', border: '1px solid #1a1a3a', color: '#fff', fontSize: 12 }}
          />
          <input placeholder="Endpoint" value={agents.agent2.endpoint}
            onChange={e => setAgents(p => ({...p, agent2: {...p.agent2, endpoint: e.target.value}}))}
            style={{ width: '100%', margin: '4px 0', padding: 6, background: '#050510', border: '1px solid #1a1a3a', color: '#fff', fontSize: 12 }}
          />
          
          <div style={{ margin: '8px 0' }}>
            <label style={{ fontSize: 11, color: '#668' }}>Temperature: {agents.agent2.temperature}</label>
            <input type="range" min="0" max="100" value={agents.agent2.temperature * 100}
              onChange={e => setAgents(p => ({...p, agent2: {...p.agent2, temperature: e.target.value / 100}}))}
              style={{ width: '100%' }}
            />
          </div>

          <button onClick={() => registerAgent(2)} disabled={agents.agent2.registered}
            style={{ width: '100%', padding: 6, background: agents.agent2.registered ? '#003322' : '#009955', border: 'none', color: '#fff', fontSize: 12 }}>
            {agents.agent2.registered ? "✓ CONNECTED" : "CONNECT"}
          </button>

          <div style={{ marginTop: 10, padding: 8, background: '#050510', minHeight: 80, fontSize: 11, color: '#88a' }}>
            {selectedAgentPrompts.agent2 || "Idle"}
          </div>

          <button onClick={() => overrideAgent(2)} style={{ width: '100%', marginTop: 8, padding: 4, background: '#331100', border: 'none', color: '#fa0', fontSize: 11 }}>
            ⌨️ MANUAL OVERRIDE
          </button>
        </div>
      </div>

      {/* BOTTOM AGENT 3 PANEL */}
      <div style={{ 
        marginTop: 12, background: '#0a0a1a', padding: 10, borderRadius: 4, border: agents.agent3.registered ? '1px solid #ff6644' : '1px solid #1a1a3a' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 200px', gap: 12, alignItems: 'center' }}>
          <div>
            <div style={{ color: '#ff6644', fontWeight: 'bold' }}>🔴 AGENT 3 (MÖBIUS OBSERVER)</div>
            <div style={{ fontSize: 11, color: '#667' }}>Non-orientable verification node</div>
          </div>
          <input placeholder="Name" value={agents.agent3.name}
            onChange={e => setAgents(p => ({...p, agent3: {...p.agent3, name: e.target.value}}))}
            style={{ padding: 6, background: '#050510', border: '1px solid #1a1a3a', color: '#fff', fontSize: 12 }}
          />
          <input placeholder="Endpoint" value={agents.agent3.endpoint}
            onChange={e => setAgents(p => ({...p, agent3: {...p.agent3, endpoint: e.target.value}}))}
            style={{ padding: 6, background: '#050510', border: '1px solid #1a1a3a', color: '#fff', fontSize: 12 }}
          />
          <button onClick={() => registerAgent(3)} disabled={agents.agent3.registered}
            style={{ padding: 6, background: agents.agent3.registered ? '#332200' : '#cc5522', border: 'none', color: '#fff', fontSize: 12 }}>
            {agents.agent3.registered ? "✓ OBSERVER ACTIVE" : "ACTIVATE OBSERVER"}
          </button>
        </div>
      </div>

      {/* STATUS BAR */}
      <div style={{ 
        marginTop: 12, display: 'flex', justifyContent: 'space-between',
        background: '#0a0a1a', padding: '8px 12px', borderRadius: 4, fontSize: 11, color: '#668'
      }}>
        <div>STATUS: {systemStatus}</div>
        <div>CONNECTED: {Object.values(agents).filter(a => a.registered).length} / 3</div>
        <div>TWIST COUNT: {(round * 0.5}</div>
        <div>NORIENTATION: {round % 2 === 0 ? "NORMAL" : "INVERTED"}</div>
      </div>
    </div>
  )
}
