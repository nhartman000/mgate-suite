/**
 * App.jsx — Kadmon 1st Order Multiplayer World
 * Panels: Lobby | Players | System Rack | Chat | Kadmon Negotiation
 * All calls wired to real FastAPI endpoints.
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import KadmonWorld from './KadmonWorld';

const API = '';   // same-origin (proxied by Vite)

async function api(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(API + path, opts);
  if (!res.ok) {
    const t = await res.text();
    throw new Error(`${res.status} ${t}`);
  }
  return res.json();
}

/* ------------------------------------------------------------------ */
/*  Colour helpers                                                      */
/* ------------------------------------------------------------------ */
const TYPE_COLOR = {
  human:      '#ffff00',
  llm_gpt:    '#00aaff',
  llm_claude: '#ff6600',
  llm_gemini: '#00ff88',
  llm_grok:   '#cc00ff',
  llm_custom: '#ffffff',
};

const ORDER_COLOR = {
  1: '#ff4444',
  2: '#ff8800',
  3: '#00aaff',
  4: '#00ff88',
  5: '#cc44ff',
};

const STATUS_COLOR = {
  installed: '#888888',
  enabled:   '#00ff88',
  disabled:  '#ff4444',
  error:     '#ff0000',
};

/* ------------------------------------------------------------------ */
/*  Small UI atoms                                                      */
/* ------------------------------------------------------------------ */
const Pill = ({ label, color = '#888' }) => (
  <span style={{
    display: 'inline-block', padding: '1px 7px', borderRadius: 9999,
    background: color + '33', border: `1px solid ${color}`,
    color, fontSize: 10, fontWeight: 700, letterSpacing: 0.5,
  }}>{label}</span>
);

const Btn = ({ children, onClick, color = '#333', disabled = false, small = false }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    style={{
      padding: small ? '3px 10px' : '6px 14px',
      fontSize: small ? 11 : 12,
      background: disabled ? '#222' : color,
      color: disabled ? '#555' : '#fff',
      border: `1px solid ${disabled ? '#333' : color}`,
      borderRadius: 4,
      cursor: disabled ? 'default' : 'pointer',
      fontFamily: 'monospace',
    }}
  >
    {children}
  </button>
);

const Input = ({ value, onChange, placeholder, style = {} }) => (
  <input
    value={value}
    onChange={e => onChange(e.target.value)}
    placeholder={placeholder}
    style={{
      background: '#1a1a1a', border: '1px solid #444', color: '#eee',
      padding: '5px 8px', borderRadius: 4, fontFamily: 'monospace',
      fontSize: 12, ...style,
    }}
  />
);

const Select = ({ value, onChange, options, style = {} }) => (
  <select
    value={value}
    onChange={e => onChange(e.target.value)}
    style={{
      background: '#1a1a1a', border: '1px solid #444', color: '#eee',
      padding: '5px 8px', borderRadius: 4, fontFamily: 'monospace', fontSize: 12, ...style,
    }}
  >
    {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
  </select>
);

const Section = ({ title, children }) => (
  <div style={{ marginBottom: 18 }}>
    <div style={{
      fontSize: 10, letterSpacing: 2, color: '#666', textTransform: 'uppercase',
      marginBottom: 8, borderBottom: '1px solid #222', paddingBottom: 4,
    }}>{title}</div>
    {children}
  </div>
);

/* ------------------------------------------------------------------ */
/*  PlayerRow                                                           */
/* ------------------------------------------------------------------ */
function PlayerRow({ player, worldId, onAction, selected, onSelect }) {
  const [chatMsg, setChatMsg] = useState('');
  const [loading, setLoading] = useState(false);

  const sendChat = async () => {
    if (!chatMsg.trim()) return;
    setLoading(true);
    try {
      await api('POST', `/api/worlds/${worldId}/players/${player.player_id}/chat`,
        { player_id: player.player_id, message: chatMsg });
      setChatMsg('');
    } catch (e) { alert(e.message); }
    finally { setLoading(false); }
  };

  const respond = async () => {
    setLoading(true);
    try {
      await api('POST', `/api/worlds/${worldId}/players/${player.player_id}/respond`,
        { player_id: player.player_id, context: 'Current Kadmon negotiation context.' });
      onAction();
    } catch (e) { alert(e.message); }
    finally { setLoading(false); }
  };

  const remove = async () => {
    setLoading(true);
    try {
      await api('DELETE', `/api/worlds/${worldId}/players/${player.player_id}`);
      onAction();
    } catch (e) { alert(e.message); }
    finally { setLoading(false); }
  };

  const color = TYPE_COLOR[player.entity_type] || '#888';

  return (
    <div
      onClick={() => onSelect(player.player_id)}
      style={{
        background: selected ? '#1a2a1a' : '#111',
        border: `1px solid ${selected ? color : '#333'}`,
        borderRadius: 6, padding: '8px 10px', marginBottom: 8,
        cursor: 'pointer',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{ color, fontSize: 16 }}>●</span>
          <span style={{ color: '#eee', fontWeight: 700, fontSize: 12 }}>{player.name}</span>
          <Pill label={player.entity_type} color={color} />
          {player.negotiation_role && <Pill label={player.negotiation_role} color="#ffaa00" />}
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {player.entity_type !== 'human' && (
            <Btn small color="#005577" onClick={e => { e.stopPropagation(); respond(); }} disabled={loading}>
              LLM Respond
            </Btn>
          )}
          <Btn small color="#550000" onClick={e => { e.stopPropagation(); remove(); }} disabled={loading}>
            Remove
          </Btn>
        </div>
      </div>
      <div style={{ color: '#555', fontSize: 10, marginTop: 4 }}>
        pos ({player.position?.real?.toFixed(4)}, {player.position?.imag?.toFixed(4)}) ·
        msgs: {player.message_count}
      </div>
      {selected && player.entity_type === 'human' && (
        <div style={{ display: 'flex', gap: 6, marginTop: 8 }} onClick={e => e.stopPropagation()}>
          <Input value={chatMsg} onChange={setChatMsg} placeholder="Message…" style={{ flex: 1 }} />
          <Btn small color="#005500" onClick={sendChat} disabled={loading || !chatMsg.trim()}>Send</Btn>
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Add Player Form                                                     */
/* ------------------------------------------------------------------ */
function AddPlayerForm({ worldId, onAdded }) {
  const [form, setForm]   = useState({
    player_id: '', name: '', entity_type: 'human', model: '', system_prompt: '',
  });
  const [types, setTypes] = useState([]);
  const [busy, setBusy]   = useState(false);

  useEffect(() => {
    api('GET', '/api/player_types').then(d => setTypes(d.types)).catch(() => {});
  }, []);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const submit = async () => {
    if (!form.player_id || !form.name) return alert('Player ID and Name required');
    setBusy(true);
    try {
      const payload = {
        player_id:    form.player_id,
        name:         form.name,
        entity_type:  form.entity_type,
        model:        form.model || undefined,
        system_prompt:form.system_prompt || undefined,
      };
      await api('POST', `/api/worlds/${worldId}/players`, payload);
      setForm({ player_id: '', name: '', entity_type: 'human', model: '', system_prompt: '' });
      onAdded();
    } catch (e) { alert(e.message); }
    finally { setBusy(false); }
  };

  const typeOpts = types.map(t => ({ value: t.type, label: t.label }));
  const curType  = types.find(t => t.type === form.entity_type);

  return (
    <div style={{ background: '#0f1a0f', border: '1px solid #2a4a2a', borderRadius: 6, padding: 12 }}>
      <div style={{ color: '#88cc88', fontSize: 11, marginBottom: 10, fontWeight: 700 }}>
        + ADD PLAYER / LLM AGENT
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        <div style={{ display: 'flex', gap: 6 }}>
          <Input value={form.player_id} onChange={v => set('player_id', v)} placeholder="player_id" style={{ flex: 1 }} />
          <Input value={form.name}      onChange={v => set('name', v)}      placeholder="Display name" style={{ flex: 1 }} />
        </div>
        {typeOpts.length > 0 && (
          <Select value={form.entity_type} onChange={v => set('entity_type', v)} options={typeOpts} />
        )}
        {curType?.needs_model && (
          <Input
            value={form.model}
            onChange={v => set('model', v)}
            placeholder={`Model (default: ${curType.default_model})`}
          />
        )}
        <textarea
          value={form.system_prompt}
          onChange={e => set('system_prompt', e.target.value)}
          placeholder="Custom system prompt (optional)"
          rows={2}
          style={{
            background: '#1a1a1a', border: '1px solid #444', color: '#eee',
            padding: '5px 8px', borderRadius: 4, fontFamily: 'monospace',
            fontSize: 11, resize: 'vertical',
          }}
        />
        <Btn onClick={submit} disabled={busy} color="#226622">
          {busy ? 'Adding…' : 'Add to World'}
        </Btn>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  System Rack (VST-style)                                             */
/* ------------------------------------------------------------------ */
function SystemRackPanel({ worldId }) {
  const [available, setAvailable] = useState([]);
  const [instances, setInstances] = useState([]);
  const [filter, setFilter]       = useState('');
  const [busy, setBusy]           = useState({});

  const refresh = useCallback(async () => {
    try {
      const [avail, inst] = await Promise.all([
        api('GET', `/api/worlds/${worldId}/systems/available`),
        api('GET', `/api/worlds/${worldId}/systems`),
      ]);
      setAvailable(avail);
      setInstances(inst);
    } catch (e) { console.error(e); }
  }, [worldId]);

  useEffect(() => { refresh(); }, [refresh]);

  const setBusyKey = (k, v) => setBusy(b => ({ ...b, [k]: v }));

  const install = async (system_id) => {
    setBusyKey(system_id, true);
    try { await api('POST', `/api/worlds/${worldId}/systems/install`, { system_id }); await refresh(); }
    catch (e) { alert(e.message); }
    finally { setBusyKey(system_id, false); }
  };

  const enable = async (instance_id) => {
    setBusyKey(instance_id, true);
    try { await api('POST', `/api/worlds/${worldId}/systems/${instance_id}/enable`); await refresh(); }
    catch (e) { alert(e.message); }
    finally { setBusyKey(instance_id, false); }
  };

  const disable = async (instance_id) => {
    setBusyKey(instance_id, true);
    try { await api('POST', `/api/worlds/${worldId}/systems/${instance_id}/disable`); await refresh(); }
    catch (e) { alert(e.message); }
    finally { setBusyKey(instance_id, false); }
  };

  const uninstall = async (instance_id) => {
    setBusyKey(instance_id, true);
    try { await api('DELETE', `/api/worlds/${worldId}/systems/${instance_id}`); await refresh(); }
    catch (e) { alert(e.message); }
    finally { setBusyKey(instance_id, false); }
  };

  const installedIds = new Set(instances.map(i => i.system_id));
  const filtered     = available.filter(s =>
    !filter || s.name.toLowerCase().includes(filter.toLowerCase()) ||
    String(s.order).includes(filter)
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

      {/* Active instances — plugin rack */}
      {instances.length > 0 && (
        <Section title="Active Systems (Plugin Rack)">
          {instances.map(inst => (
            <div key={inst.instance_id} style={{
              background: '#111', border: `1px solid ${STATUS_COLOR[inst.status]}44`,
              borderLeft: `3px solid ${STATUS_COLOR[inst.status]}`,
              borderRadius: 4, padding: '7px 10px', marginBottom: 6,
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            }}>
              <div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <span style={{ color: '#eee', fontSize: 12, fontWeight: 700 }}>{inst.name}</span>
                  <Pill label={`${inst.order}th`} color={ORDER_COLOR[inst.order] || '#888'} />
                  <Pill label={inst.status} color={STATUS_COLOR[inst.status]} />
                </div>
                <div style={{ color: '#555', fontSize: 10, marginTop: 3, fontFamily: 'monospace' }}>
                  {inst.instance_id.slice(0, 16)}…
                </div>
              </div>
              <div style={{ display: 'flex', gap: 5 }}>
                {inst.status !== 'enabled' && (
                  <Btn small color="#005500" onClick={() => enable(inst.instance_id)} disabled={!!busy[inst.instance_id]}>
                    Enable
                  </Btn>
                )}
                {inst.status === 'enabled' && (
                  <Btn small color="#553300" onClick={() => disable(inst.instance_id)} disabled={!!busy[inst.instance_id]}>
                    Disable
                  </Btn>
                )}
                <Btn small color="#550000" onClick={() => uninstall(inst.instance_id)} disabled={!!busy[inst.instance_id]}>
                  ✕
                </Btn>
              </div>
            </div>
          ))}
        </Section>
      )}

      {/* Available systems catalogue */}
      <Section title="Available Systems">
        <Input value={filter} onChange={setFilter} placeholder="Filter by name or order…" style={{ width: '100%', marginBottom: 8 }} />
        {filtered.map(s => (
          <div key={s.system_id} style={{
            background: '#0d0d0d', border: '1px solid #2a2a2a',
            borderLeft: `3px solid ${ORDER_COLOR[s.order] || '#444'}`,
            borderRadius: 4, padding: '7px 10px', marginBottom: 5,
            display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
          }}>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <span style={{ color: '#ccc', fontSize: 12, fontWeight: 700 }}>{s.name}</span>
                <Pill label={`Order ${s.order}`} color={ORDER_COLOR[s.order] || '#888'} />
              </div>
              <div style={{ color: '#666', fontSize: 10, marginTop: 2 }}>{s.description}</div>
            </div>
            <Btn
              small
              color={installedIds.has(s.system_id) ? '#333' : '#004477'}
              onClick={() => install(s.system_id)}
              disabled={!!busy[s.system_id]}
            >
              {installedIds.has(s.system_id) ? 'Add Another' : 'Install'}
            </Btn>
          </div>
        ))}
      </Section>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Kadmon Negotiation Panel                                            */
/* ------------------------------------------------------------------ */
function KadmonPanel({ worldId }) {
  const [status, setStatus] = useState(null);
  const [points, setPoints] = useState({});
  const [busy, setBusy]     = useState(false);
  const [log, setLog]       = useState([]);

  const refresh = useCallback(async () => {
    try {
      const [s, p] = await Promise.all([
        api('GET', `/api/worlds/${worldId}/kadmon/status`),
        api('GET', '/api/kadmon/points'),
      ]);
      setStatus(s);
      setPoints(p);
    } catch (e) { /* not started yet */ }
  }, [worldId]);

  useEffect(() => { refresh(); }, [refresh]);

  const start = async () => {
    setBusy(true);
    try {
      await api('POST', `/api/worlds/${worldId}/kadmon/start`);
      await refresh();
    } catch (e) { alert(e.message); }
    finally { setBusy(false); }
  };

  const move = async (pointName, agentId, moveType) => {
    setBusy(true);
    try {
      const r = await api('POST', `/api/worlds/${worldId}/kadmon/move`,
        { agent_id: agentId, point_name: pointName, move_type: moveType });
      setLog(l => [{ round: r.stability?.round, agent: agentId, point: pointName, type: moveType, math: r.stability?.mathematical?.toFixed(3) }, ...l.slice(0, 19)]);
      await refresh();
    } catch (e) { alert(e.message); }
    finally { setBusy(false); }
  };

  const autoRun = async () => {
    setBusy(true);
    try {
      const r = await api('POST', `/api/worlds/${worldId}/kadmon/run`);
      setLog(l => [{ auto: true, rounds: r.rounds, complete: r.complete }, ...l.slice(0, 19)]);
      await refresh();
    } catch (e) { alert(e.message); }
    finally { setBusy(false); }
  };

  const ptNames = Object.keys(points);

  return (
    <div>
      {!status?.active && !status?.complete && (
        <Btn onClick={start} disabled={busy} color="#004477">Start Negotiation</Btn>
      )}

      {status?.active && (
        <>
          <div style={{ background: '#0d1a0d', border: '1px solid #1a4a1a', borderRadius: 6, padding: 10, marginBottom: 10 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
              <span style={{ color: '#00ff88', fontSize: 12 }}>Round {status.round}</span>
              <span style={{ color: '#88ff88', fontSize: 12 }}>
                Math stability: {status.mathematical?.toFixed(4)}
              </span>
            </div>
            <div style={{ fontSize: 10, color: '#666', fontFamily: 'monospace' }}>
              <div>Problem: ({status.problem_position?.real?.toFixed(5)}, {status.problem_position?.imag?.toFixed(5)})</div>
              <div>Agent1:  ({status.agent1_position?.real?.toFixed(5)}, {status.agent1_position?.imag?.toFixed(5)})</div>
              <div>Agent2:  ({status.agent2_position?.real?.toFixed(5)}, {status.agent2_position?.imag?.toFixed(5)})</div>
            </div>
          </div>

          <Section title="Manual Moves">
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 8 }}>
              {ptNames.map(pt => (
                <Btn key={pt} small color="#003355" onClick={() => move(pt, 'agent_1', 'move_self')} disabled={busy}>
                  A1→{pt}
                </Btn>
              ))}
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 8 }}>
              {ptNames.map(pt => (
                <Btn key={pt} small color="#330044" onClick={() => move(pt, 'agent_2', 'move_self')} disabled={busy}>
                  A2→{pt}
                </Btn>
              ))}
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 8 }}>
              {ptNames.map(pt => (
                <Btn key={pt} small color="#443300" onClick={() => move(pt, 'agent_1', 'move_problem')} disabled={busy}>
                  P→{pt}
                </Btn>
              ))}
            </div>
          </Section>

          <Btn onClick={autoRun} disabled={busy} color="#225500">Auto-Run (LLM agents)</Btn>
        </>
      )}

      {status?.complete && (
        <div style={{ color: '#00ff88', padding: 10, background: '#001a00', borderRadius: 6, marginBottom: 10 }}>
          ✓ Consensus reached at ({status.agreed_position?.real?.toFixed(5)}, {status.agreed_position?.imag?.toFixed(5)})
        </div>
      )}

      {log.length > 0 && (
        <Section title="Move Log">
          <div style={{ maxHeight: 150, overflowY: 'auto', fontFamily: 'monospace', fontSize: 10 }}>
            {log.map((l, i) => (
              <div key={i} style={{ color: '#556655', borderBottom: '1px solid #111', padding: '2px 0' }}>
                {l.auto
                  ? `AUTO-RUN: ${l.rounds} rounds, complete=${l.complete}`
                  : `R${l.round} ${l.agent} ${l.type}→${l.point} math=${l.math}`
                }
              </div>
            ))}
          </div>
        </Section>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Chat Feed                                                           */
/* ------------------------------------------------------------------ */
function ChatFeed({ worldId }) {
  const [msgs, setMsgs] = useState([]);
  const bottomRef = useRef(null);

  useEffect(() => {
    if (!worldId) return;
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${proto}://${window.location.host}/ws/world/${worldId}`);
    ws.onmessage = ev => {
      const msg = JSON.parse(ev.data);
      if (msg.type === 'chat') {
        setMsgs(m => [...m.slice(-99), msg.message]);
      }
      if (msg.type === 'snapshot') {
        setMsgs(msg.world?.chat_log || []);
      }
    };
    return () => ws.close();
  }, [worldId]);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [msgs]);

  const color = m => TYPE_COLOR[m.entity_type] || (m.role === 'assistant' ? '#00aaff' : '#ffff00');

  return (
    <div style={{ flex: 1, overflowY: 'auto', fontFamily: 'monospace', fontSize: 11 }}>
      {msgs.length === 0 && <div style={{ color: '#444', padding: 10 }}>No messages yet.</div>}
      {msgs.map(m => (
        <div key={m.id} style={{ padding: '4px 6px', borderBottom: '1px solid #111' }}>
          <span style={{ color: color(m), fontWeight: 700 }}>{m.player_id}</span>
          <span style={{ color: '#555' }}> [{m.role}] </span>
          <span style={{ color: '#bbb' }}>{m.content}</span>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Lobby                                                              */
/* ------------------------------------------------------------------ */
function Lobby({ onEnter }) {
  const [worlds, setWorlds] = useState([]);
  const [name, setName]     = useState('');
  const [busy, setBusy]     = useState(false);

  const refresh = () => api('GET', '/api/worlds').then(setWorlds).catch(() => {});
  useEffect(() => { refresh(); }, []);

  const createWorld = async () => {
    setBusy(true);
    try {
      const w = await api('POST', '/api/worlds', { name: name || undefined });
      onEnter(w.world_id);
    } catch (e) { alert(e.message); }
    finally { setBusy(false); }
  };

  return (
    <div style={{
      minHeight: '100vh', background: '#0d0d0d', display: 'flex',
      flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'monospace', color: '#eee',
    }}>
      <h1 style={{ color: '#00ff88', letterSpacing: 4, marginBottom: 4 }}>KADMON</h1>
      <div style={{ color: '#666', marginBottom: 40, letterSpacing: 2, fontSize: 12 }}>
        1ST ORDER MULTIPLAYER WORLD
      </div>

      <div style={{ width: 440, background: '#111', border: '1px solid #333', borderRadius: 8, padding: 24 }}>
        <Section title="Create New World">
          <div style={{ display: 'flex', gap: 8 }}>
            <Input value={name} onChange={setName} placeholder="World name (optional)" style={{ flex: 1 }} />
            <Btn onClick={createWorld} disabled={busy} color="#004477">
              {busy ? '…' : 'Create + Enter'}
            </Btn>
          </div>
        </Section>

        {worlds.length > 0 && (
          <Section title="Existing Worlds">
            {worlds.map(w => (
              <div key={w.world_id} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                background: '#0d0d0d', border: '1px solid #2a2a2a', borderRadius: 4,
                padding: '7px 10px', marginBottom: 6,
              }}>
                <div>
                  <div style={{ color: '#eee', fontSize: 12 }}>{w.name}</div>
                  <div style={{ color: '#555', fontSize: 10 }}>
                    {w.players} players · {w.entities} entities
                  </div>
                </div>
                <Btn small color="#005577" onClick={() => onEnter(w.world_id)}>Enter</Btn>
              </div>
            ))}
          </Section>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main App                                                            */
/* ------------------------------------------------------------------ */
const TABS = ['players', 'systems', 'negotiation', 'chat'];

export default function App() {
  const [worldId,  setWorldId]  = useState(null);
  const [players,  setPlayers]  = useState([]);
  const [selected, setSelected] = useState(null);
  const [tab,      setTab]      = useState('players');
  const worldRef = useRef(null);

  const refreshPlayers = useCallback(async () => {
    if (!worldId) return;
    try {
      const p = await api('GET', `/api/worlds/${worldId}/players`);
      setPlayers(p);
    } catch (e) { console.error(e); }
  }, [worldId]);

  useEffect(() => {
    if (!worldId) return;
    refreshPlayers();
  }, [worldId, refreshPlayers]);

  // Forward world-click events to selected human player
  const onWorldClick = useCallback(async (e) => {
    const { real, imag } = e.detail;
    if (!selected || !worldId) return;
    const p = players.find(p => p.player_id === selected);
    if (!p || p.entity_type !== 'human') return;
    try {
      await api('POST', `/api/worlds/${worldId}/players/${selected}/move`,
        { player_id: selected, real, imag, z: 0 });
      refreshPlayers();
    } catch (e) { console.error(e); }
  }, [selected, players, worldId, refreshPlayers]);

  useEffect(() => {
    const el = worldRef.current;
    if (!el) return;
    el.addEventListener('world-click', onWorldClick);
    return () => el.removeEventListener('world-click', onWorldClick);
  }, [onWorldClick]);

  if (!worldId) return <Lobby onEnter={id => setWorldId(id)} />;

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', background: '#0d0d0d', fontFamily: 'monospace', overflow: 'hidden' }}>

      {/* ---- 3D Viewport ---- */}
      <div ref={worldRef} style={{ flex: 1, position: 'relative' }}>
        <KadmonWorld worldId={worldId} />

        {/* Viewport overlay — axis legend */}
        <div style={{
          position: 'absolute', bottom: 16, left: 16,
          background: 'rgba(0,0,0,0.7)', border: '1px solid #333',
          borderRadius: 6, padding: '8px 12px', fontSize: 10, color: '#888',
          pointerEvents: 'none',
        }}>
          <div style={{ color: '#ff4444', marginBottom: 2 }}>▶ X  Real axis</div>
          <div style={{ color: '#44ff44', marginBottom: 2 }}>▲ Y  Imaginary axis</div>
          <div style={{ color: '#4488ff', marginBottom: 2 }}>◆ Z  Stability axis</div>
          <div style={{ color: '#ffaa00', marginTop: 6 }}>C = −0.500003 (invariant center)</div>
          <div style={{ color: '#555', marginTop: 4 }}>Click ground plane to move selected player</div>
        </div>

        {/* World ID badge */}
        <div style={{
          position: 'absolute', top: 10, left: 10,
          background: 'rgba(0,0,0,0.6)', padding: '4px 10px',
          borderRadius: 4, color: '#555', fontSize: 10,
        }}>
          {worldId}
        </div>
      </div>

      {/* ---- Right Panel ---- */}
      <div style={{
        width: 360, display: 'flex', flexDirection: 'column',
        background: '#0f0f0f', borderLeft: '1px solid #222', overflow: 'hidden',
      }}>

        {/* Tab bar */}
        <div style={{ display: 'flex', borderBottom: '1px solid #222' }}>
          {TABS.map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              style={{
                flex: 1, padding: '10px 4px', fontSize: 10, letterSpacing: 1,
                textTransform: 'uppercase', border: 'none',
                background: tab === t ? '#1a1a1a' : 'transparent',
                color: tab === t ? '#00ff88' : '#555',
                borderBottom: tab === t ? '2px solid #00ff88' : '2px solid transparent',
                cursor: 'pointer', fontFamily: 'monospace',
              }}
            >{t}</button>
          ))}
        </div>

        {/* Tab content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 14 }}>

          {tab === 'players' && (
            <>
              <AddPlayerForm worldId={worldId} onAdded={refreshPlayers} />
              <div style={{ marginTop: 14 }}>
                <Section title={`Players (${players.length})`}>
                  {players.length === 0 && (
                    <div style={{ color: '#444', fontSize: 11 }}>No players yet.</div>
                  )}
                  {players.map(p => (
                    <PlayerRow
                      key={p.player_id}
                      player={p}
                      worldId={worldId}
                      onAction={refreshPlayers}
                      selected={selected === p.player_id}
                      onSelect={setSelected}
                    />
                  ))}
                </Section>
              </div>
            </>
          )}

          {tab === 'systems' && (
            <SystemRackPanel worldId={worldId} />
          )}

          {tab === 'negotiation' && (
            <KadmonPanel worldId={worldId} />
          )}

          {tab === 'chat' && (
            <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              <ChatFeed worldId={worldId} />
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          borderTop: '1px solid #222', padding: '8px 14px',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <span style={{ color: '#333', fontSize: 10 }}>KADMON 1ST ORDER</span>
          <Btn small color="#330000" onClick={() => setWorldId(null)}>← Lobby</Btn>
        </div>
      </div>
    </div>
  );
}
