import React, { useState, useCallback } from 'react'

const ORDER_COLOR = '#cc88ff'
const BG_DARK = '#0a0020'
const BG_MID = '#0d0028'
const BORDER = '#3a1a5a'

const OPERATORS = ['align', 'check', 'shift', 'amplify', 'interrupt', 'stabilize']

const OPERATOR_ICONS = {
  align:     '🎯',
  check:     '✅',
  shift:     '↗️',
  amplify:   '📡',
  interrupt: '⚡',
  stabilize: '🔒',
}

function StabilityMeter({ value }) {
  const pct = Math.min(1, Math.max(0, value))
  const color = pct > 0.8 ? '#00ff88' : pct > 0.5 ? '#ffaa44' : '#ff4455'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      <div style={{
        flex: 1,
        height: 6,
        background: '#1a0a2a',
        borderRadius: 3,
        overflow: 'hidden',
        border: '1px solid #2a1a3a'
      }}>
        <div style={{
          width: `${pct * 100}%`,
          height: '100%',
          background: color,
          borderRadius: 3,
          transition: 'width 0.4s ease, background 0.4s ease',
          boxShadow: `0 0 6px ${color}88`
        }} />
      </div>
      <span style={{ color, fontFamily: 'monospace', fontSize: 10, minWidth: 36 }}>
        {(pct * 100).toFixed(0)}%
      </span>
    </div>
  )
}

function TokenChip({ token }) {
  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 3,
      background: '#15003a',
      border: '1px solid #3a1a5a',
      borderRadius: 4,
      padding: '2px 6px',
      margin: '2px',
      fontSize: 11,
      fontFamily: 'monospace',
      color: ORDER_COLOR,
    }}>
      <span style={{ fontSize: 14 }}>{token.emoji}</span>
      <span style={{ color: '#6633aa', fontSize: 9 }}>{token.consonants}</span>
      <span style={{ color: '#443355', fontSize: 9 }}>{token.word}</span>
    </div>
  )
}

export default function NychPanel({ onNychResult }) {
  const [open, setOpen] = useState(false)
  const [inputText, setInputText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeOps, setActiveOps] = useState(new Set())
  const [injectHeader, setInjectHeader] = useState(false)
  const [error, setError] = useState(null)

  const toggleOp = (op) => {
    setActiveOps(prev => {
      const next = new Set(prev)
      if (next.has(op)) next.delete(op)
      else next.add(op)
      return next
    })
  }

  const processText = useCallback(async () => {
    if (!inputText.trim()) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/nych/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText, inject_header: injectHeader })
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setResult(data)
      if (onNychResult) onNychResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [inputText, injectHeader, onNychResult])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      processText()
    }
  }

  return (
    <div style={{
      background: BG_DARK,
      border: `1px solid ${BORDER}`,
      borderRadius: 6,
      marginBottom: 16,
      fontFamily: 'monospace',
      fontSize: 12,
      overflow: 'hidden'
    }}>
      {/* VST Plugin Header */}
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          width: '100%',
          padding: '10px 14px',
          background: BG_MID,
          border: 'none',
          borderBottom: open ? `1px solid ${BORDER}` : 'none',
          color: ORDER_COLOR,
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
          {/* VST-style power LED */}
          <span style={{
            width: 8, height: 8, borderRadius: '50%',
            background: result ? '#cc88ff' : '#33114a',
            boxShadow: result ? '0 0 8px #cc88ff' : 'none',
            display: 'inline-block',
            flexShrink: 0
          }} />
          <span style={{ color: '#6633aa' }}>◈</span>
          {' '}NYCH — 5TH ORDER GESTALT ENCODER
          <span style={{
            fontSize: 9,
            color: '#442266',
            border: '1px solid #3a1a5a',
            padding: '1px 5px',
            borderRadius: 3,
            marginLeft: 4
          }}>VST</span>
        </span>
        <span style={{ color: '#442266', fontSize: 10 }}>{open ? '▲ COLLAPSE' : '▼ EXPAND'}</span>
      </button>

      {open && (
        <div style={{ padding: '12px 14px' }}>

          {/* OPERATOR RACK — VST-style toggle buttons */}
          <div style={{ marginBottom: 10 }}>
            <div style={{ color: '#442266', fontSize: 10, letterSpacing: 1, marginBottom: 5 }}>
              ── OPERATOR RACK ──
            </div>
            <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap' }}>
              {OPERATORS.map(op => (
                <button
                  key={op}
                  onClick={() => toggleOp(op)}
                  style={{
                    padding: '4px 8px',
                    background: activeOps.has(op) ? '#2a0055' : '#0a0018',
                    border: `1px solid ${activeOps.has(op) ? ORDER_COLOR : '#2a1a3a'}`,
                    color: activeOps.has(op) ? ORDER_COLOR : '#442266',
                    fontFamily: 'monospace',
                    fontSize: 10,
                    cursor: 'pointer',
                    borderRadius: 3,
                    boxShadow: activeOps.has(op) ? `0 0 6px ${ORDER_COLOR}44` : 'none',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {OPERATOR_ICONS[op]} {op}
                </button>
              ))}
            </div>
          </div>

          {/* INPUT / OUTPUT — Audio plugin I/O style */}
          <div style={{ marginBottom: 8 }}>
            <div style={{ color: '#442266', fontSize: 10, letterSpacing: 1, marginBottom: 4 }}>
              ── INPUT ──
            </div>
            <div style={{ display: 'flex', gap: 6 }}>
              <textarea
                value={inputText}
                onChange={e => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Enter natural language text... (Enter to encode)"
                rows={2}
                style={{
                  flex: 1,
                  background: '#050012',
                  border: `1px solid ${BORDER}`,
                  color: '#ccaaff',
                  fontFamily: 'monospace',
                  fontSize: 11,
                  padding: 8,
                  borderRadius: 3,
                  resize: 'vertical',
                  outline: 'none',
                }}
              />
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                <button
                  onClick={processText}
                  disabled={loading || !inputText.trim()}
                  style={{
                    padding: '8px 12px',
                    background: loading ? '#1a0030' : '#2a0055',
                    border: `1px solid ${loading ? '#220044' : ORDER_COLOR}`,
                    color: loading ? '#442266' : ORDER_COLOR,
                    fontFamily: 'monospace',
                    fontSize: 10,
                    fontWeight: 'bold',
                    cursor: loading ? 'default' : 'pointer',
                    borderRadius: 3,
                    letterSpacing: 1,
                    boxShadow: loading ? 'none' : `0 0 8px ${ORDER_COLOR}33`,
                    whiteSpace: 'nowrap'
                  }}
                >
                  {loading ? '⟳ ENC...' : '▶ ENCODE'}
                </button>
                <label style={{
                  display: 'flex', alignItems: 'center', gap: 4,
                  color: '#442266', fontSize: 9, cursor: 'pointer'
                }}>
                  <input
                    type="checkbox"
                    checked={injectHeader}
                    onChange={e => setInjectHeader(e.target.checked)}
                    style={{ accentColor: ORDER_COLOR }}
                  />
                  HDR INJ
                </label>
              </div>
            </div>
          </div>

          {error && (
            <div style={{ color: '#ff4455', fontSize: 10, marginBottom: 6, padding: '4px 8px', background: '#1a0008', border: '1px solid #550022', borderRadius: 3 }}>
              ⚠ {error} — is api/server.py running?
            </div>
          )}

          {result && (
            <>
              {/* SYMBOL STREAM OUTPUT */}
              <div style={{ marginBottom: 8 }}>
                <div style={{ color: '#442266', fontSize: 10, letterSpacing: 1, marginBottom: 4 }}>
                  ── OUTPUT — SYMBOL STREAM ──
                </div>
                <div style={{
                  background: '#050012',
                  border: `1px solid ${BORDER}`,
                  borderRadius: 3,
                  padding: 8,
                  fontFamily: 'monospace',
                  fontSize: 11,
                  color: '#bb88ff',
                  wordBreak: 'break-all',
                  lineHeight: 1.6,
                  maxHeight: 80,
                  overflowY: 'auto',
                }}>
                  {result.symbol_stream}
                </div>
              </div>

              {/* TOKEN CHIPS */}
              {result.tokens && result.tokens.length > 0 && (
                <div style={{ marginBottom: 8 }}>
                  <div style={{ color: '#442266', fontSize: 10, letterSpacing: 1, marginBottom: 4 }}>
                    ── TOKEN MAP ──
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                    {result.tokens.map((t, i) => <TokenChip key={i} token={t} />)}
                  </div>
                </div>
              )}

              {/* STABILITY METER */}
              <div style={{ marginBottom: 8 }}>
                <div style={{ color: '#442266', fontSize: 10, letterSpacing: 1, marginBottom: 4 }}>
                  ── GESTALT STABILITY ──
                </div>
                <StabilityMeter value={result.stability} />
              </div>

              {/* DOMAIN ANALYSIS */}
              <div style={{ marginBottom: 8 }}>
                <div style={{ color: '#442266', fontSize: 10, letterSpacing: 1, marginBottom: 4 }}>
                  ── DOMAIN ANALYSIS ──
                </div>
                <div style={{
                  background: '#060015',
                  border: `1px solid #1a0a2a`,
                  borderRadius: 3,
                  padding: 8,
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 4
                }}>
                  <div>
                    <span style={{ color: '#331155', fontSize: 10 }}>MODALITY: </span>
                    <span style={{ color: '#aa66ff', fontSize: 11 }}>
                      {result.domain?.modality?.join(' ') || '—'}
                    </span>
                  </div>
                  <div>
                    <span style={{ color: '#331155', fontSize: 10 }}>ORDER: </span>
                    <span style={{ color: ORDER_COLOR, fontSize: 11 }}>{result.order}</span>
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <span style={{ color: '#331155', fontSize: 10 }}>TOTE LOOPS: </span>
                    <span style={{ color: result.domain?.tote_loops?.length > 0 ? '#ffaa44' : '#331155', fontSize: 11 }}>
                      {result.domain?.tote_loops?.length > 0
                        ? result.domain.tote_loops.join(' → ')
                        : 'none detected'}
                    </span>
                  </div>
                  {injectHeader && result.header && (
                    <div style={{ gridColumn: '1 / -1' }}>
                      <div style={{ color: '#331155', fontSize: 10, marginBottom: 2 }}>INJECTED HEADER:</div>
                      <div style={{
                        color: '#664488',
                        fontSize: 9,
                        fontFamily: 'monospace',
                        background: '#030010',
                        padding: '4px 6px',
                        borderRadius: 3,
                        maxHeight: 60,
                        overflowY: 'auto',
                        wordBreak: 'break-all'
                      }}>
                        {result.header?.slice(0, 200)}...
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </>
          )}

          {!result && !loading && (
            <div style={{ color: '#221133', fontSize: 10, fontStyle: 'italic', textAlign: 'center', padding: '8px 0' }}>
              No signal — enter text and press ENCODE
            </div>
          )}

        </div>
      )}
    </div>
  )
}
