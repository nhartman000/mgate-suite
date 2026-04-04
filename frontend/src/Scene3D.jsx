import React, { useRef, useMemo, useState, useEffect } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Line, Sphere, Text } from '@react-three/drei'
import * as THREE from 'three'
import { vertexShader, fragmentShader } from './MandelbulbShader'

const ScreenQuad = ({ children }) => {
  return (
    <mesh>
      <planeGeometry args={[2, 2]} />
      {children}
    </mesh>
  )
}

const MandelbulbBackground = () => {
  const { size, camera } = useThree()
  const materialRef = useRef()

  const uniforms = useMemo(() => ({
    time: { value: 0 },
    resolution: { value: new THREE.Vector2(size.width, size.height) },
    cameraPos: { value: new THREE.Vector3() },
    cameraWorldMatrix: { value: new THREE.Matrix4() },
    cameraProjectionMatrixInverse: { value: new THREE.Matrix4() }
  }), [])

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uniforms.time.value = state.clock.elapsedTime
      materialRef.current.uniforms.resolution.value.set(size.width, size.height)
      materialRef.current.uniforms.cameraPos.value.copy(camera.position)
      materialRef.current.uniforms.cameraWorldMatrix.value.copy(camera.matrixWorld)
      materialRef.current.uniforms.cameraProjectionMatrixInverse.value.copy(camera.projectionMatrixInverse)
    }
  })

  // Returns a full screen pass quad since vertex shader fixes z to 1.0
  return (
    <mesh>
      <planeGeometry args={[2, 2]} />
      <shaderMaterial
        ref={materialRef}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        depthWrite={false}
      />
    </mesh>
  )
}

const CenterSphere = ({ position }) => {
  const matRef = useRef()
  useFrame((state) => {
    if (matRef.current) {
      const t = state.clock.elapsedTime
      matRef.current.emissiveIntensity = 0.3 + 0.7 * (0.5 + 0.5 * Math.sin(t * 2.0))
    }
  })
  return (
    <Sphere position={position} args={[0.04, 16, 16]}>
      <meshStandardMaterial
        ref={matRef}
        color="#ff00ff"
        emissive="#ff00ff"
        emissiveIntensity={0.3}
        transparent
        opacity={0.75}
      />
    </Sphere>
  )
}

const Triangulation = ({ user, query, ai, iu, center }) => {
  if (!user || !query || !ai) return null;
  const points = [user, query, ai, user]
  return (
    <group>
      <Line points={points} color="cyan" lineWidth={2} />
      
      <Sphere position={user} args={[0.05, 16, 16]}>
        <meshStandardMaterial color="blue" />
      </Sphere>
      <Text position={[user[0], user[1] + 0.1, user[2]]} fontSize={0.1} color="white">USER</Text>

      <Sphere position={query} args={[0.05, 16, 16]}>
        <meshStandardMaterial color="orange" />
      </Sphere>
      <Text position={[query[0], query[1] + 0.1, query[2]]} fontSize={0.1} color="white">QUERY</Text>

      <Sphere position={ai} args={[0.08, 16, 16]}>
        <meshStandardMaterial color="green" />
      </Sphere>
      <Text position={[ai[0], ai[1] + 0.1, ai[2]]} fontSize={0.1} color="white">AI</Text>

      {iu && (
        <>
          <Sphere position={iu} args={[0.06, 16, 16]}>
            <meshStandardMaterial color="#ffff00" />
          </Sphere>
          <Text position={[iu[0], iu[1] + 0.1, iu[2]]} fontSize={0.1} color="white">IU</Text>
        </>
      )}

      {center && (
        <>
          <CenterSphere position={center} />
          <Text position={[center[0], center[1] + 0.08, center[2]]} fontSize={0.1} color="white">C</Text>
        </>
      )}
    </group>
  )
}

const MANDELBROT_POINTS = [
  { pos: [-0.75,     0.0,    0], color: '#334455', size: 0.02 },  // container
  { pos: [-0.75,     0.125,  0], color: '#334455', size: 0.02 },  // triangle_upper
  { pos: [-0.75,    -0.125,  0], color: '#334455', size: 0.02 },  // triangle_lower
  { pos: [-0.875,    0.2165, 0], color: '#223344', size: 0.02 },  // bulb_upper_center
  { pos: [-0.875,   -0.2165, 0], color: '#223344', size: 0.02 },  // bulb_lower_center
  { pos: [-0.500003, 0.0,    0], color: '#ffdd00', size: 0.03 },  // stability_anchor (C - bright)
  { pos: [-1.31,     0.0,    0], color: '#334455', size: 0.02 },  // user_anchor
]

const KadmonGeometry = () => {
  // Triangle points: container -> triangle_upper -> triangle_lower -> container
  const trianglePoints = [
    MANDELBROT_POINTS[0].pos,
    MANDELBROT_POINTS[1].pos,
    MANDELBROT_POINTS[2].pos,
    MANDELBROT_POINTS[0].pos,
  ]

  return (
    <group>
      <Line points={trianglePoints} color="#112233" lineWidth={1} />
      {MANDELBROT_POINTS.map((pt, i) => (
        <Sphere key={i} position={pt.pos} args={[pt.size, 8, 8]}>
          <meshStandardMaterial color={pt.color} />
        </Sphere>
      ))}
    </group>
  )
}

const AgentPositions = ({ negotiationPositions }) => {
  if (!negotiationPositions) return null
  const agentColors = ['#00aaff', '#00ff88', '#ff88ff', '#ff8800', '#ff4444']
  const entries = Object.entries(negotiationPositions)

  return (
    <group>
      {entries.map(([agentId, pos], i) => {
        const color = agentColors[i % agentColors.length]
        return (
          <group key={agentId}>
            <Sphere position={pos} args={[0.035, 16, 16]}>
              <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.6} />
            </Sphere>
            <Text position={[pos[0], pos[1] + 0.07, pos[2]]} fontSize={0.07} color={color}>
              {agentId}
            </Text>
          </group>
        )
      })}
    </group>
  )
}

const Mandelbrot2D = () => {
  const canvasRef = useRef()
  const [iterationCount, setIterationCount] = useState(100)
  
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    const width = canvas.width
    const height = canvas.height
    
    const imageData = ctx.createImageData(width, height)
    const data = imageData.data
    
    const xMin = -2.5
    const xMax = 1.0
    const yMin = -1.5
    const yMax = 1.5
    
    for (let px = 0; px < width; px++) {
      for (let py = 0; py < height; py++) {
        const x0 = xMin + (px / width) * (xMax - xMin)
        const y0 = yMin + (py / height) * (yMax - yMin)
        
        let x = 0
        let y = 0
        let iter = 0
        
        while (x * x + y * y <= 4 && iter < iterationCount) {
          const xTemp = x * x - y * y + x0
          y = 2 * x * y + y0
          x = xTemp
          iter++
        }
        
        const idx = (py * width + px) * 4
        if (iter === iterationCount) {
          data[idx] = 0
          data[idx + 1] = 0
          data[idx + 2] = 0
          data[idx + 3] = 255
        } else {
          const hue = (iter / iterationCount) * 360
          const rgb = hslToRgb(hue / 360, 1, 0.5)
          data[idx] = rgb[0]
          data[idx + 1] = rgb[1]
          data[idx + 2] = rgb[2]
          data[idx + 3] = 255
        }
      }
    }
    
    ctx.putImageData(imageData, 0, 0)
  }, [iterationCount])
  
  return (
    <group>
      <mesh position={[0, 0, 0]} rotation={[0, 0, 0]}>
        <planeGeometry args={[5, 3.5]} />
        <meshBasicMaterial>
          <canvas ref={canvasRef} width={500} height={350} style={{ display: 'none' }} />
        </meshBasicMaterial>
      </mesh>
      <Text position={[-2.3, -1.5, 0]} fontSize={0.15} color="#00ff88" anchorX="left" anchorY="bottom">
        MANDELBROT SET (2D attractor)
      </Text>
    </group>
  )
}
        
        const idx = (py * width + px) * 4
        if (iter === iterationCount) {
          data[idx] = 0
          data[idx + 1] = 0
          data[idx + 2] = 0
          data[idx + 3] = 255
        } else {
          const hue = (iter / iterationCount) * 360
          const rgb = hslToRgb(hue / 360, 1, 0.5)
          data[idx] = rgb[0]
          data[idx + 1] = rgb[1]
          data[idx + 2] = rgb[2]
          data[idx + 3] = 255
        }
      }
    }
    
    ctx.putImageData(imageData, 0, 0)
  }, [iterationCount])
  
  return (
    <group>
      <mesh position={[0, 0, 0]} rotation={[0, 0, 0]}>
        <planeGeometry args={[5, 3.5]} />
        <meshBasicMaterial>
          <canvas ref={canvasRef} width={500} height={350} style={{ display: 'none' }} />
        </meshBasicMaterial>
      </mesh>
      <Text position={[-2.3, -1.5, 0]} fontSize={0.15} color="#00ff88" anchorX="left" anchorY="bottom">
        MANDELBROT SET (2D attractor)
      </Text>
    </group>
  )
}

function hslToRgb(h, s, l) {
  let r, g, b
  
  if (s === 0) {
    r = g = b = l
  } else {
    const hue2rgb = (p, q, t) => {
      if (t < 0) t += 1
      if (t > 1) t -= 1
      if (t < 1/6) return p + (q - p) * 6 * t
      if (t < 1/2) return q
      if (t < 2/3) return p + (q - p) * (2/3 - t) * 6
      return p
    }
    
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s
    const p = 2 * l - q
    r = hue2rgb(p, q, h + 1/3)
    g = hue2rgb(p, q, h)
    b = hue2rgb(p, q, h - 1/3)
  }
  
  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)]
}

export default function Scene3D({ user, query, ai, iu, center, negotiationPositions, view2D }) {
  return (
    <Canvas camera={{ position: view2D ? [0, 0, 0.01] : [0, 0, 5] }} style={{ background: '#000', width: '100%', height: '100%' }}>
      {!view2D && <ambientLight intensity={0.5} />}
      {!view2D && <pointLight position={[10, 10, 10]} />}
      {!view2D && <OrbitControls />}
      {view2D ? <Mandelbrot2D /> : <MandelbulbBackground />}
      <KadmonGeometry />
      <AgentPositions negotiationPositions={negotiationPositions} />
      <Triangulation user={user} query={query} ai={ai} iu={iu} center={center} />
    </Canvas>
  )
}
