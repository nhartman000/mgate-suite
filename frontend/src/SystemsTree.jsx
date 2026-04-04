import React, { useState, useEffect, useCallback, useRef } from 'react'

const ORDER_COLORS = {
  1: '#00ffaa',
  2: '#00aaff',
  3: '#00ff88',
  4: '#ffaa44',
  5: '#cc88ff',
}

const ORDER_BG = {
  1: '#001a0d',
  2: '#001533',
  3: '#001a0d',
  4: '#1a0d00',
  5: '#0d0020',
}

const ORDER_LABELS = {
  1: '1st',
  2: '2nd',
  3: '3rd',
  4: '4th',
  5: '5th',
}

function SystemNode({ node, selected, onSelect, onDragStart, onDelete }) {
  const color = ORDER_COLORS[node.order] ?? '#778899'
  const bg = ORDER_BG[node.order] ?? '#0a0a1a'

  return (
    <div
      onMouseDown={e => { e.stopPropagation(); onDragStart(e, node.id); onSelect(node.id) }}
      onClick={e => { e.stopPropagation(); onSelect(node.id) }}
      style={{
        position: 'absolute',
        left: node.position.x,
        top: node.position.y,
        minWidth: 140,
        maxWidth: 180,
        background: bg,
        border: `2px solid ${selected ? color : color + '55'}`,
        borderRadius: 6,
        padding: '8px 10px',
        cursor: node.locked ? 'default' : 'grab',
        userSelect: 'none',
        boxShadow: selected ? `0 0 14px ${color}44` : `0 0 4px ${color}22`,
        transition: 'box-shadow 0.2s ease, border-color 0.2s ease',
        zIndex: selected ? 10 : 5,
        fontFamily: 'monospace',
      }}
    >
      {/* Order badge */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
        <span style={{
          fontSize: 9,
          color: color,
          border: `1px solid ${color}44`,
          padding: '1px 4px',
          borderRadius: 3,
          letterSpacing: 1,
          background: color + '11'
        }}>
          {ORDER_LABELS[node.order] ?? node.order} ORDER
        </span>
        {!node.locked && (
          <button
            onMouseDown={e => e.stopPropagation()}
            onClick={e => { e.stopPropagation(); onDelete(node.id) }}
            style={{
              background: 'none',
              border: 'none',
              color: '#552233',
              cursor: 'pointer',
              fontSize: 10,
              padding: '0 2px',
              lineHeight: 1,
            }}
            title="Remove node"
          >
            ✕
          </button>
        )}
        {node.locked && (
          <span style={{ fontSize: 9, color: '#334455' }}>🔒</span>
        )}
      </div>

      {/* Label */}
      <div style={{ color, fontSize: 11, fontWeight: 'bold', letterSpacing: 0.5, marginBottom: 3, wordBreak: 'break-word' }}>
        {node.label}
      </div>

      {/* Description */}
      <div style={{ color: '#445566', fontSize: 9, lineHeight: 1.4, wordBreak: 'break-word' }}>
        {node.description?.slice(0, 60)}{node.description?.length > 60 ? '…' : ''}
      </div>
    </div>
  )
}

function EdgeLayer({ nodes, edges, canvasW, canvasH }) {
  const nodeMap = {}
  for (const n of nodes) {
    // Approximate center of node (node width ~160, height ~80)
    nodeMap[n.id] = {
      x: n.position.x + 80,
      y: n.position.y + 50,
    }
  }

  return (
    <svg
      style={{ position: 'absolute', top: 0, left: 0, width: canvasW, height: canvasH, pointerEvents: 'none', zIndex: 1 }}
    >
      <defs>
        <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
          <path d="M0,0 L0,6 L8,3 z" fill="#334455" />
        </marker>
      </defs>
      {edges.map(edge => {
        const src = nodeMap[edge.source]
        const tgt = nodeMap[edge.target]
        if (!src || !tgt) return null
        const dx = tgt.x - src.x
        const dy = tgt.y - src.y
        // Bezier control points
        const cx1 = src.x + dx * 0.25
        const cy1 = src.y + dy * 0.75
        const cx2 = src.x + dx * 0.75
        const cy2 = src.y + dy * 0.25
        const srcColor = ORDER_COLORS[nodes.find(n => n.id === edge.source)?.order] ?? '#334455'
        return (
          <path
            key={edge.id}
            d={`M ${src.x} ${src.y} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${tgt.x} ${tgt.y}`}
            stroke={srcColor + '66'}
            strokeWidth={1.5}
            fill="none"
            markerEnd="url(#arrow)"
          />
        )
      })}
    </svg>
  )
}

function AddNodeSidebar({ onAdd, visible, onToggle }) {
  const [label, setLabel] = useState('')
  const [order, setOrder] = useState(3)
  const [description, setDescription] = useState('')

  const handleAdd = () => {
    if (!label.trim()) return
    onAdd({
      id: `node_${Date.now()}`,
      type: 'system',
      order,
      label: label.trim(),
      description: description.trim(),
      color: ORDER_COLORS[order] ?? '#778899',
      position: { x: 100 + Math.random() * 400, y: 100 + Math.random() * 300 },
      locked: false
    })
    setLabel('')
    setDescription('')
  }

  if (!visible) return null

  return (
    <div style={{
      position: 'absolute',
      right: 8,
      top: 8,
      width: 180,
      background: '#080818',
      border: '1px solid #1a2a3a',
      borderRadius: 6,
      padding: 12,
      fontFamily: 'monospace',
      fontSize: 11,
      zIndex: 20,
    }}>
      <div style={{ color: '#00aaff', fontWeight: 'bold', marginBottom: 8, fontSize: 10, letterSpacing: 1 }}>
        + ADD SYSTEM NODE
      </div>

      <div style={{ marginBottom: 6 }}>
        <div style={{ color: '#445566', fontSize: 9, marginBottom: 3 }}>ORDER</div>
        <select
          value={order}
          onChange={e => setOrder(Number(e.target.value))}
          style={{
            width: '100%', background: '#050512', border: '1px solid #1a2a3a',
            color: ORDER_COLORS[order] ?? '#778899', fontFamily: 'monospace', fontSize: 11, padding: 4
          }}
        >
          {[2, 3, 4, 5].map(o => (
            <option key={o} value={o}>{ORDER_LABELS[o]} Order</option>
          ))}
        </select>
      </div>

      <div style={{ marginBottom: 6 }}>
        <div style={{ color: '#445566', fontSize: 9, marginBottom: 3 }}>LABEL</div>
        <input
          value={label}
          onChange={e => setLabel(e.target.value)}
          placeholder="System name"
          onKeyDown={e => e.key === 'Enter' && handleAdd()}
          style={{
            width: '100%', background: '#050512', border: '1px solid #1a2a3a',
            color: '#ccddf0', fontFamily: 'monospace', fontSize: 11, padding: 4,
            boxSizing: 'border-box'
          }}
        />
      </div>

      <div style={{ marginBottom: 8 }}>
        <div style={{ color: '#445566', fontSize: 9, marginBottom: 3 }}>DESCRIPTION</div>
        <input
          value={description}
          onChange={e => setDescription(e.target.value)}
          placeholder="Short description"
          style={{
            width: '100%', background: '#050512', border: '1px solid #1a2a3a',
            color: '#7799aa', fontFamily: 'monospace', fontSize: 10, padding: 4,
            boxSizing: 'border-box'
          }}
        />
      </div>

      <button
        onClick={handleAdd}
        disabled={!label.trim()}
        style={{
          width: '100%', padding: '6px 0',
          background: label.trim() ? '#0a1a2a' : '#050510',
          border: `1px solid ${label.trim() ? '#00aaff' : '#1a2a3a'}`,
          color: label.trim() ? '#00aaff' : '#334455',
          fontFamily: 'monospace', fontSize: 10, fontWeight: 'bold',
          cursor: label.trim() ? 'pointer' : 'default',
          borderRadius: 3, letterSpacing: 1
        }}
      >
        ADD NODE
      </button>
    </div>
  )
}

export default function SystemsTree({ installedPlugins }) {
  const [open, setOpen] = useState(false)
  const [nodes, setNodes] = useState([])
  const [edges, setEdges] = useState([])
  const [selected, setSelected] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [saveTimeout, setSaveTimeout] = useState(null)

  // Drag state
  const dragging = useRef(null)
  const canvasRef = useRef(null)
  const CANVAS_W = 900
  const CANVAS_H = 750

  // Load tree from API
  const loadTree = useCallback(async () => {
    try {
      const res = await fetch('/api/systems/tree')
      if (res.ok) {
        const data = await res.json()
        setNodes(data.nodes || [])
        setEdges(data.edges || [])
      }
    } catch (e) {
      // API not available — use minimal default
      setNodes([
        { id: 'kadmon_1st', type: 'system', order: 1, label: 'KADMON RUNTIME', description: '1st Order — Invariant center C = -0.500003', color: '#00ffaa', position: { x: 340, y: 20 }, locked: true },
        { id: 'pair_2nd', type: 'system', order: 2, label: 'PAIR / COUPLE', description: '2nd Order — Dual LLM config', color: '#00aaff', position: { x: 340, y: 140 }, locked: false },
        { id: 'llm_3rd', type: 'system', order: 3, label: 'LLM Backends [3rd]', description: '3rd Order — GPT / Claude / Gemini / Grok', color: '#00ff88', position: { x: 340, y: 280 }, locked: false },
        { id: 'mgate_4th', type: 'system', order: 4, label: 'MGATE / MCP / TMT [4th]', description: '4th Order — DAG + Memory + Möbius', color: '#ffaa44', position: { x: 340, y: 420 }, locked: false },
        { id: 'nych_5th', type: 'system', order: 5, label: 'NYCH [5th]', description: '5th Order — Gestalt encoder', color: '#cc88ff', position: { x: 340, y: 560 }, locked: false },
      ])
      setEdges([
        { id: 'e1', source: 'kadmon_1st', target: 'pair_2nd' },
        { id: 'e2', source: 'pair_2nd', target: 'llm_3rd' },
        { id: 'e3', source: 'llm_3rd', target: 'mgate_4th' },
        { id: 'e4', source: 'mgate_4th', target: 'nych_5th' },
      ])
    }
  }, [])

  useEffect(() => {
    if (open) loadTree()
  }, [open, loadTree])

  // Auto-save tree state (debounced)
  const saveTree = useCallback((newNodes, newEdges) => {
    if (saveTimeout) clearTimeout(saveTimeout)
    const t = setTimeout(async () => {
      try {
        await fetch('/api/systems/tree', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ nodes: newNodes, edges: newEdges })
        })
      } catch (e) {}
    }, 600)
    setSaveTimeout(t)
  }, [saveTimeout])

  // Drag handlers
  const handleDragStart = useCallback((e, nodeId) => {
    const node = nodes.find(n => n.id === nodeId)
    if (!node || node.locked) return
    const rect = canvasRef.current?.getBoundingClientRect()
    if (!rect) return
    dragging.current = {
      nodeId,
      startX: e.clientX,
      startY: e.clientY,
      origX: node.position.x,
      origY: node.position.y,
    }
  }, [nodes])

  const handleMouseMove = useCallback((e) => {
    if (!dragging.current) return
    const { nodeId, startX, startY, origX, origY } = dragging.current
    const dx = e.clientX - startX
    const dy = e.clientY - startY
    setNodes(prev => prev.map(n =>
      n.id === nodeId
        ? { ...n, position: { x: Math.max(0, origX + dx), y: Math.max(0, origY + dy) } }
        : n
    ))
  }, [])

  const handleMouseUp = useCallback(() => {
    if (dragging.current) {
      dragging.current = null
      // Save after drag ends
      setNodes(prev => {
        saveTree(prev, edges)
        return prev
      })
    }
  }, [edges, saveTree])

  const handleAddNode = useCallback((node) => {
    const newNodes = [...nodes, node]
    setNodes(newNodes)
    saveTree(newNodes, edges)
  }, [nodes, edges, saveTree])

  const handleDeleteNode = useCallback(async (nodeId) => {
    try {
      await fetch(`/api/systems/tree/node/${nodeId}`, { method: 'DELETE' })
    } catch (e) {}
    const newNodes = nodes.filter(n => n.id !== nodeId)
    const newEdges = edges.filter(e => e.source !== nodeId && e.target !== nodeId)
    setNodes(newNodes)
    setEdges(newEdges)
    if (selected === nodeId) setSelected(null)
    saveTree(newNodes, newEdges)
  }, [nodes, edges, selected, saveTree])

  const handleReset = useCallback(async () => {
    setLoading(true)
    try {
      await fetch('/api/systems/tree/reset', { method: 'POST' })
      await loadTree()
    } catch (e) {
      await loadTree()
    } finally {
      setLoading(false)
    }
  }, [loadTree])

  const selectedNode = nodes.find(n => n.id === selected)

  return (
    <div style={{
      background: '#060616',
      border: '1px solid #1a2a3a',
      borderRadius: 6,
      marginBottom: 16,
      fontFamily: 'monospace',
      fontSize: 12,
      overflow: 'hidden'
    }}>
      {/* Header */}
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          width: '100%',
          padding: '10px 14px',
          background: '#080820',
          border: 'none',
          borderBottom: open ? '1px solid #1a2a3a' : 'none',
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
        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ color: '#334455' }}>◈</span>
          SYSTEMS TREE — ORDER HIERARCHY FLOWCHART
          <span style={{ fontSize: 9, color: '#223344', border: '1px solid #223344', padding: '1px 4px', borderRadius: 3 }}>
            {nodes.length} nodes
          </span>
        </span>
        <span style={{ color: '#334455', fontSize: 10 }}>{open ? '▲ COLLAPSE' : '▼ EXPAND'}</span>
      </button>

      {open && (
        <div>
          {/* Toolbar */}
          <div style={{
            display: 'flex',
            gap: 8,
            padding: '8px 12px',
            background: '#070718',
            borderBottom: '1px solid #1a2a3a',
            alignItems: 'center'
          }}>
            <button
              onClick={() => setSidebarOpen(o => !o)}
              style={{
                padding: '4px 10px',
                background: sidebarOpen ? '#0a1a2a' : '#050510',
                border: `1px solid ${sidebarOpen ? '#00aaff' : '#1a2a3a'}`,
                color: sidebarOpen ? '#00aaff' : '#445566',
                fontFamily: 'monospace',
                fontSize: 10,
                cursor: 'pointer',
                borderRadius: 3,
              }}
            >
              + ADD NODE
            </button>
            <button
              onClick={handleReset}
              disabled={loading}
              style={{
                padding: '4px 10px',
                background: '#050510',
                border: '1px solid #1a2a3a',
                color: '#445566',
                fontFamily: 'monospace',
                fontSize: 10,
                cursor: 'pointer',
                borderRadius: 3,
              }}
            >
              {loading ? '⟳' : '↺'} RESET
            </button>
            <button
              onClick={loadTree}
              style={{
                padding: '4px 10px',
                background: '#050510',
                border: '1px solid #1a2a3a',
                color: '#445566',
                fontFamily: 'monospace',
                fontSize: 10,
                cursor: 'pointer',
                borderRadius: 3,
              }}
            >
              ↻ RELOAD
            </button>
            <div style={{ flex: 1 }} />
            <span style={{ color: '#223344', fontSize: 9 }}>drag nodes to rearrange · click to select · ✕ to remove</span>
          </div>

          {/* Selected node info */}
          {selectedNode && (
            <div style={{
              padding: '6px 12px',
              background: '#060615',
              borderBottom: '1px solid #1a2a3a',
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              fontSize: 10
            }}>
              <span style={{ color: ORDER_COLORS[selectedNode.order] ?? '#778899', fontWeight: 'bold' }}>
                ▶ {selectedNode.label}
              </span>
              <span style={{ color: '#334455' }}>|</span>
              <span style={{ color: '#445566' }}>{ORDER_LABELS[selectedNode.order]} Order</span>
              <span style={{ color: '#334455' }}>|</span>
              <span style={{ color: '#334455', flex: 1 }}>{selectedNode.description}</span>
              <span style={{ color: '#223344' }}>
                ({Math.round(selectedNode.position.x)}, {Math.round(selectedNode.position.y)})
              </span>
            </div>
          )}

          {/* Canvas */}
          <div
            ref={canvasRef}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onClick={() => setSelected(null)}
            style={{
              position: 'relative',
              width: '100%',
              height: CANVAS_H,
              background: '#050510',
              overflow: 'hidden',
              cursor: 'default',
              backgroundImage: `
                radial-gradient(circle at 1px 1px, #0a1020 1px, transparent 0)
              `,
              backgroundSize: '24px 24px',
            }}
          >
            {/* Grid overlay */}
            <svg style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', opacity: 0.12 }}>
              <defs>
                <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
                  <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#1a2a3a" strokeWidth="0.5"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
            </svg>

            <EdgeLayer nodes={nodes} edges={edges} canvasW={CANVAS_W} canvasH={CANVAS_H} />

            {nodes.map(node => (
              <SystemNode
                key={node.id}
                node={node}
                selected={selected === node.id}
                onSelect={setSelected}
                onDragStart={handleDragStart}
                onDelete={handleDeleteNode}
              />
            ))}

            <AddNodeSidebar
              visible={sidebarOpen}
              onToggle={() => setSidebarOpen(o => !o)}
              onAdd={handleAddNode}
            />

            {nodes.length === 0 && (
              <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                color: '#1a2a3a',
                fontSize: 13,
                fontFamily: 'monospace',
                textAlign: 'center',
                pointerEvents: 'none'
              }}>
                <div>No nodes loaded</div>
                <div style={{ fontSize: 10, marginTop: 4 }}>Click RELOAD to fetch from API</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
