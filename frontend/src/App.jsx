import React, { useState, useEffect, useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'
import { vertexShader, fragmentShader } from './MandelbulbShader'

function MandelbulbBackground() {
  const meshRef = useRef()
  const uniforms = useMemo(() => ({
    time: { value: 0 },
    resolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) }
  }), [])

  useFrame((state) => {
    uniforms.time.value = state.clock.elapsedTime
  })

  useEffect(() => {
    const handleResize = () => {
      uniforms.resolution.value.set(window.innerWidth, window.innerHeight)
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [uniforms])

  return (
    <mesh ref={meshRef} position={[0, 0, -3]}>
      <planeGeometry args={[10, 10]} />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        depthWrite={false}
      />
    </mesh>
  )
}

function AgentPoint({ position, color, size = 0.05 }) {
  const meshRef = useRef()
  const targetPos = useRef(new THREE.Vector3(...position))

  useFrame(() => {
    targetPos.current.lerp(new THREE.Vector3(...position), 0.15)
    meshRef.current.position.copy(targetPos.current)
  })

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[size, 32, 32]} />
      <meshBasicMaterial color={color} />
    </mesh>
  )
}

function AlignmentTriangle({ user, query, ai, stability }) {
  const geometry = useMemo(() => new THREE.BufferGeometry(), [])

  useFrame(() => {
    const positions = new Float32Array([
      ...user,
      ...query,
      ...ai
    ])
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geometry.computeVertexNormals()
  })

  const opacity = 0.2 + stability * 0.6

  return (
    <mesh>
      <primitive object={geometry} attach="geometry" />
      <meshBasicMaterial
        color={new THREE.Color(0, 1, 0.7)}
        transparent
        opacity={opacity}
        side={THREE.DoubleSide}
      />
    </mesh>
  )
}

function Scene({ data }) {
  return (
    <>
      <MandelbulbBackground />
      
      <AgentPoint position={data.user} color="#00aaff" size={0.04} />
      <AgentPoint position={data.query} color="#ffaa00" size={0.04} />
      <AgentPoint position={data.ai} color="#00ff88" size={0.05} />
      
      <AlignmentTriangle
        user={data.user}
        query={data.query}
        ai={data.ai}
        stability={data.stability}
      />
      
      <OrbitControls
        enablePan={false}
        minDistance={2}
        maxDistance={8}
        autoRotate
        autoRotateSpeed={0.3}
      />
    </>
  )
}

export default function App() {
  const [data, setData] = useState({
    round: 0,
    user: [-1.0, 0.0, 0.2],
    query: [-0.75, 0.0, 0.2],
    ai: [-0.500003, 0.0, 0.2],
    alignment_gap: 0.5,
    stability: 0.5
  })

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/negotiate')

    ws.onmessage = (event) => {
      const newData = JSON.parse(event.data)
      setData(newData)
    }

    ws.onopen = () => {
      console.log('WebSocket connected')
      ws.send(JSON.stringify({ x: -0.5, y: 0.0, z: 0.0 }))
    }

    return () => ws.close()
  }, [])

  return (
    <>
      <div className="hud">
        <div>ROUND: {data.round}</div>
        <div>STABILITY: {(data.stability * 100).toFixed(1)}%</div>
        <div>ALIGNMENT GAP: {data.alignment_gap.toFixed(4)}</div>
        <div>CENTER: -0.500003</div>
      </div>

      <Canvas camera={{ position: [0, 0, 4], fov: 60 }}>
        <Scene data={data} />
      </Canvas>
    </>
  )
}
