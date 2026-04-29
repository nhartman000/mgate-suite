/**
 * KadmonWorld.jsx
 * 3-plane AutoCAD/Maya-style grid + live multiplayer world rendering.
 * All API calls are wired to the backend.
 */
import React, { useEffect, useRef, useCallback } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

/* -------------------------------------------------------------------------- */
/*  Grid helpers                                                               */
/* -------------------------------------------------------------------------- */

/** Build a line-based grid for one plane.
 *  axis: 'xy' | 'xz' | 'yz'
 *  size: half-extent,  divisions: # of lines per side
 */
function buildGrid(axis, size = 2, divisions = 20, colorMain = 0x444444, colorSub = 0x222222) {
  const step   = (size * 2) / divisions;
  const lines  = [];
  const half   = size;

  for (let i = 0; i <= divisions; i++) {
    const t     = -half + i * step;
    const color = i === divisions / 2 ? colorMain : colorSub;
    const mat   = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.6 });

    let pts;
    if (axis === 'xy') {
      // vertical lines (X fixed, sweep Y)
      pts = [new THREE.Vector3(t, -half, 0), new THREE.Vector3(t, half, 0)];
      lines.push(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat));
      // horizontal lines
      pts = [new THREE.Vector3(-half, t, 0), new THREE.Vector3(half, t, 0)];
      lines.push(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat));

    } else if (axis === 'xz') {
      pts = [new THREE.Vector3(t, 0, -half), new THREE.Vector3(t, 0, half)];
      lines.push(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat));
      pts = [new THREE.Vector3(-half, 0, t), new THREE.Vector3(half, 0, t)];
      lines.push(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat));

    } else if (axis === 'yz') {
      pts = [new THREE.Vector3(0, t, -half), new THREE.Vector3(0, t, half)];
      lines.push(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat));
      pts = [new THREE.Vector3(0, -half, t), new THREE.Vector3(0, half, t)];
      lines.push(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat));
    }
  }

  const group = new THREE.Group();
  lines.forEach(l => group.add(l));
  return group;
}

/** Transparent fill-plane (ghost panel like AutoCAD's grid fill). */
function buildPlaneGhost(axis, size = 2, color = 0x1a3a5c) {
  const geo  = new THREE.PlaneGeometry(size * 2, size * 2);
  const mat  = new THREE.MeshBasicMaterial({
    color, transparent: true, opacity: 0.06,
    side: THREE.DoubleSide, depthWrite: false,
  });
  const mesh = new THREE.Mesh(geo, mat);
  if (axis === 'xz') mesh.rotation.x = -Math.PI / 2;
  if (axis === 'yz') mesh.rotation.y = -Math.PI / 2;
  return mesh;
}

/** Canvas-text sprite for axis/tick labels. */
function makeTextSprite(text, color = '#ffffff', fontSize = 14) {
  const canvas  = document.createElement('canvas');
  canvas.width  = 256;
  canvas.height = 64;
  const ctx     = canvas.getContext('2d');
  ctx.fillStyle = 'transparent';
  ctx.clearRect(0, 0, 256, 64);
  ctx.font      = `bold ${fontSize}px monospace`;
  ctx.fillStyle = color;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 128, 32);
  const tex = new THREE.CanvasTexture(canvas);
  const spr = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false }));
  spr.scale.set(0.5, 0.125, 1);
  return spr;
}

/** Tick marks + numbers along one axis. */
function buildTickMarks(axis, size = 2, step = 0.25) {
  const group = new THREE.Group();
  for (let v = -size; v <= size + 0.001; v += step) {
    const rounded = Math.round(v * 100) / 100;
    if (rounded === 0) continue;
    const sprite = makeTextSprite(String(rounded), '#888888', 10);
    if (axis === 'x') sprite.position.set(v, -0.07, 0);
    if (axis === 'y') sprite.position.set(-0.07, v, 0);
    if (axis === 'z') sprite.position.set(0, -0.07, v);
    group.add(sprite);
  }
  return group;
}

/* -------------------------------------------------------------------------- */
/*  Entity mesh factory                                                        */
/* -------------------------------------------------------------------------- */
const ENTITY_COLORS = {
  human:            0xffff00,
  llm_gpt:          0x00aaff,
  llm_claude:       0xff6600,
  llm_gemini:       0x00ff88,
  llm_grok:         0xcc00ff,
  llm_custom:       0xffffff,
  kadmon_anchor:    0x888888,
  spawn_point:      0x00ff00,
};

function buildEntityMesh(entity) {
  const isPlayer = !!entity.entity_type &&
    ['human', 'llm_gpt', 'llm_claude', 'llm_gemini', 'llm_grok', 'llm_custom'].includes(entity.entity_type);

  const color = ENTITY_COLORS[entity.entity_type] ?? 0x888888;
  let geo, mat;

  if (isPlayer) {
    geo = new THREE.SphereGeometry(0.04, 16, 16);
    mat = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.3 });
  } else if (entity.entity_type === 'kadmon_anchor') {
    geo = new THREE.OctahedronGeometry(0.035, 0);
    mat = new THREE.MeshStandardMaterial({ color: 0x888888, wireframe: true });
  } else {
    geo = new THREE.BoxGeometry(0.04, 0.04, 0.04);
    mat = new THREE.MeshStandardMaterial({ color });
  }

  const mesh = new THREE.Mesh(geo, mat);
  mesh.userData.entityId = entity.entity_id || entity.player_id;
  mesh.userData.label    = entity.label || entity.name || entity.entity_type;
  return mesh;
}

/* -------------------------------------------------------------------------- */
/*  Main component                                                             */
/* -------------------------------------------------------------------------- */
export default function KadmonWorld({ worldId }) {
  const mountRef    = useRef(null);
  const stateRef    = useRef({
    scene: null, camera: null, renderer: null,
    controls: null, entityMeshes: {}, playerMeshes: {},
    labelSprites: {}, animFrameId: null,
  });

  /* ---- scene init ---- */
  useEffect(() => {
    if (!mountRef.current || !worldId) return;
    const el = mountRef.current;
    const s  = stateRef.current;

    /* renderer */
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(el.clientWidth, el.clientHeight);
    renderer.setClearColor(0x0d0d0d);
    el.appendChild(renderer.domElement);
    s.renderer = renderer;

    /* scene */
    const scene = new THREE.Scene();
    s.scene = scene;

    /* camera — isometric-ish start */
    const camera = new THREE.PerspectiveCamera(60, el.clientWidth / el.clientHeight, 0.001, 100);
    camera.position.set(1.5, 1.2, 1.8);
    camera.lookAt(0, 0, 0);
    s.camera = camera;

    /* orbit */
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.target.set(0, 0, 0);
    s.controls = controls;

    /* lighting */
    scene.add(new THREE.AmbientLight(0xffffff, 0.5));
    const dir = new THREE.DirectionalLight(0xffffff, 0.8);
    dir.position.set(2, 3, 2);
    scene.add(dir);

    /* ------------------------------------------------------------------ */
    /*  THREE-PLANE GRID  (AutoCAD / Maya style)                           */
    /* ------------------------------------------------------------------ */

    // XZ plane  (ground / "floor") — cyan tint
    const xzGrid = buildGrid('xz', 2, 20, 0x006666, 0x003333);
    scene.add(xzGrid);
    scene.add(buildPlaneGhost('xz', 2, 0x004444));

    // XY plane  (front wall) — green tint
    const xyGrid = buildGrid('xy', 2, 20, 0x004400, 0x002200);
    scene.add(xyGrid);
    scene.add(buildPlaneGhost('xy', 2, 0x002200));

    // YZ plane  (side wall) — blue tint
    const yzGrid = buildGrid('yz', 2, 20, 0x000066, 0x000033);
    scene.add(yzGrid);
    scene.add(buildPlaneGhost('yz', 2, 0x000044));

    /* ------------------------------------------------------------------ */
    /*  AXES  (fat colored lines with labels)                              */
    /* ------------------------------------------------------------------ */
    const axes = new THREE.AxesHelper(2.1);
    scene.add(axes);

    // Axis endpoint labels
    const xLbl = makeTextSprite('X  Real', '#ff4444', 14);
    xLbl.position.set(2.2, 0, 0);
    scene.add(xLbl);

    const yLbl = makeTextSprite('Y  Imaginary', '#44ff44', 14);
    yLbl.position.set(0, 2.2, 0);
    scene.add(yLbl);

    const zLbl = makeTextSprite('Z  Stability', '#4488ff', 14);
    zLbl.position.set(0, 0, 2.2);
    scene.add(zLbl);

    // Origin label
    const oLbl = makeTextSprite('C = -0.500003', '#ffaa00', 11);
    oLbl.position.set(0.1, 0.08, 0);
    scene.add(oLbl);

    // Tick marks on each axis
    scene.add(buildTickMarks('x', 2, 0.25));
    scene.add(buildTickMarks('y', 2, 0.25));
    scene.add(buildTickMarks('z', 2, 0.25));

    /* ------------------------------------------------------------------ */
    /*  Kadmon anchor point indicators (rings)                             */
    /* ------------------------------------------------------------------ */
    const anchors = [
      { label: 'container',        pos: [-0.75,     0,      0], color: 0x00aaff },
      { label: 'stability_anchor', pos: [-0.500003, 0,      0], color: 0x00ff88 },
      { label: 'triangle_upper',   pos: [-0.75,     0.125,  0], color: 0xffaa00 },
      { label: 'triangle_lower',   pos: [-0.75,    -0.125,  0], color: 0xffaa00 },
      { label: 'bulb_upper',       pos: [-0.875,    0.2165, 0], color: 0xff4444 },
      { label: 'bulb_lower',       pos: [-0.875,   -0.2165, 0], color: 0xff4444 },
    ];

    anchors.forEach(({ label, pos, color }) => {
      const ring = new THREE.Mesh(
        new THREE.TorusGeometry(0.03, 0.006, 8, 24),
        new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.5 })
      );
      ring.position.set(...pos);
      scene.add(ring);

      const lbl = makeTextSprite(label, '#' + color.toString(16).padStart(6, '0'), 11);
      lbl.position.set(pos[0] + 0.07, pos[1] + 0.06, pos[2]);
      scene.add(lbl);
    });

    /* ------------------------------------------------------------------ */
    /*  Origin cross-hair                                                  */
    /* ------------------------------------------------------------------ */
    ['x', 'y', 'z'].forEach((ax, i) => {
      const pts = [new THREE.Vector3(), new THREE.Vector3()];
      pts[0][ax] = -0.05; pts[1][ax] = 0.05;
      const line = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color: 0xffffff, linewidth: 2 })
      );
      scene.add(line);
    });

    /* ------------------------------------------------------------------ */
    /*  Resize handler                                                     */
    /* ------------------------------------------------------------------ */
    const onResize = () => {
      camera.aspect = el.clientWidth / el.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(el.clientWidth, el.clientHeight);
    };
    window.addEventListener('resize', onResize);

    /* ------------------------------------------------------------------ */
    /*  Animate                                                            */
    /* ------------------------------------------------------------------ */
    const animate = () => {
      s.animFrameId = requestAnimationFrame(animate);
      controls.update();
      // Gently rotate anchor rings
      scene.traverse(obj => {
        if (obj.isMesh && obj.geometry?.type === 'TorusGeometry') {
          obj.rotation.z += 0.005;
        }
      });
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(s.animFrameId);
      window.removeEventListener('resize', onResize);
      controls.dispose();
      renderer.dispose();
      if (el.contains(renderer.domElement)) el.removeChild(renderer.domElement);
    };
  }, [worldId]);

  /* ---- sync world state → meshes via WebSocket ---- */
  useEffect(() => {
    if (!worldId) return;
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${proto}://${window.location.host}/ws/world/${worldId}`);

    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.type === 'snapshot' || msg.type === 'world_update') {
        syncEntitiesToScene(msg.world);
      }
      if (msg.type === 'player_moved') {
        moveMeshById(msg.player_id, msg.position);
      }
    };

    // Request updates every 2 s
    const tick = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN)
        ws.send(JSON.stringify({ action: 'snapshot' }));
    }, 2000);

    return () => { clearInterval(tick); ws.close(); };
  }, [worldId]);

  /* ---- helpers ---- */
  const syncEntitiesToScene = useCallback((world) => {
    if (!world || !stateRef.current.scene) return;
    const s = stateRef.current;

    // Players
    (world.players || []).forEach(player => {
      const key = player.player_id;
      if (!s.playerMeshes[key]) {
        const mesh = buildEntityMesh({ ...player, entity_type: player.entity_type });
        s.scene.add(mesh);
        s.playerMeshes[key] = mesh;

        const lbl = makeTextSprite(
          `${player.name} [${player.entity_type}]`,
          player.entity_type === 'human' ? '#ffff00' : '#00aaff', 12
        );
        s.scene.add(lbl);
        s.labelSprites[key] = lbl;
      }
      const pos = player.position;
      s.playerMeshes[key].position.set(pos.real, pos.imag, pos.z || 0);
      s.labelSprites[key].position.set(pos.real + 0.06, pos.imag + 0.06, pos.z || 0);
    });

    // World entities
    (world.entities || []).forEach(ent => {
      const key = ent.entity_id;
      if (!s.entityMeshes[key]) {
        const mesh = buildEntityMesh(ent);
        s.scene.add(mesh);
        s.entityMeshes[key] = mesh;
      }
      const pos = ent.position;
      s.entityMeshes[key].position.set(pos.real, pos.imag, pos.z || 0);
    });
  }, []);

  const moveMeshById = useCallback((playerId, pos) => {
    const mesh = stateRef.current.playerMeshes[playerId];
    const lbl  = stateRef.current.labelSprites[playerId];
    if (mesh) mesh.position.set(pos.real, pos.imag, pos.z || 0);
    if (lbl)  lbl.position.set(pos.real + 0.06, pos.imag + 0.06, pos.z || 0);
  }, []);

  /* ---- click → move (for selected human player) ---- */
  const onCanvasClick = useCallback((e) => {
    const s = stateRef.current;
    if (!s.camera || !s.scene) return;

    const el   = mountRef.current;
    const rect = el.getBoundingClientRect();
    const mouse = new THREE.Vector2(
      ((e.clientX - rect.left) / rect.width)  *  2 - 1,
      ((e.clientY - rect.top)  / rect.height) * -2 + 1,
    );
    const ray   = new THREE.Raycaster();
    ray.setFromCamera(mouse, s.camera);
    const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
    const hit   = new THREE.Vector3();
    ray.ray.intersectPlane(plane, hit);

    // Emit to parent
    el.dispatchEvent(new CustomEvent('world-click', { detail: { real: hit.x, imag: hit.y, z: 0 }, bubbles: true }));
  }, []);

  return (
    <div
      ref={mountRef}
      onClick={onCanvasClick}
      style={{ width: '100%', height: '100%', cursor: 'crosshair', background: '#0d0d0d' }}
    />
  );
}
