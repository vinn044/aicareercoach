import { Canvas, useFrame } from '@react-three/fiber'
import { useRef } from 'react'

const outerPoints = [
  [-1.9, 1.15, -0.35, 0.12],
  [-1.35, 0.7, 0.45, 0.18],
  [-0.75, 1.55, -0.25, 0.09],
  [-0.2, 1.2, 0.65, 0.14],
  [0.45, 1.45, -0.15, 0.1],
  [1.1, 1.0, 0.3, 0.17],

  [-1.7, 0.1, 0.5, 0.1],
  [-1.2, -0.3, -0.4, 0.16],
  [-0.45, 0.35, 0.25, 0.11],
  [0.15, -0.05, -0.45, 0.17],
  [0.95, 0.25, 0.6, 0.11],
  [1.5, -0.1, -0.15, 0.14],

  [-1.8, -1.0, 0.15, 0.17],
  [-1.15, -1.35, -0.45, 0.1],
  [-0.55, -0.8, 0.45, 0.13],
  [0.2, -1.0, -0.15, 0.11],
  [0.9, -0.7, 0.35, 0.16],
  [1.45, -1.1, -0.25, 0.1],
]

const innerPoints = [
  [-0.35, 0.25, -0.15, 0.085],
  [-0.18, 0.1, 0.22, 0.065],
  [0.1, 0.28, -0.05, 0.075],
  [0.28, -0.12, 0.15, 0.07],
  [-0.08, -0.22, -0.18, 0.06],
  [0.22, 0.06, -0.22, 0.055],
  [-0.22, -0.02, 0.1, 0.06],
  [0.02, -0.05, 0.02, 0.075],
]

function FloatingPoint({
  position,
  size,
  index,
  color = '#5a6d5e',
  secondaryColor = '#9aac9d',
}) {
  const pointRef = useRef()

  useFrame((state) => {
    if (!pointRef.current) return

    pointRef.current.position.y =
      position[1] + Math.sin(state.clock.elapsedTime * 0.65 + index) * 0.04
  })

  const darker = size >= 0.14

  return (
    <mesh ref={pointRef} position={position}>
      <sphereGeometry args={[size, 24, 24]} />
      <meshStandardMaterial
        color={darker ? color : secondaryColor}
        roughness={0.7}
        metalness={0}
      />
    </mesh>
  )
}

function InnerPoint({ position, size, index }) {
  const pointRef = useRef()

  useFrame((state) => {
    if (!pointRef.current) return

    pointRef.current.position.y =
      position[1] + Math.sin(state.clock.elapsedTime * 1 + index) * 0.03

    pointRef.current.position.x =
      position[0] + Math.cos(state.clock.elapsedTime * 0.7 + index) * 0.015
  })

  return (
    <mesh ref={pointRef} position={position}>
      <sphereGeometry args={[size, 20, 20]} />
      <meshStandardMaterial
        color="#6f8374"
        roughness={0.55}
        metalness={0}
      />
    </mesh>
  )
}

function PolyhedronCluster() {
  const clusterRef = useRef()

  useFrame((state, delta) => {
    if (!clusterRef.current) return

    clusterRef.current.rotation.y += delta * 0.18
    clusterRef.current.rotation.x =
      0.16 + Math.sin(state.clock.elapsedTime * 0.45) * 0.05
    clusterRef.current.position.y =
      0.25 + Math.sin(state.clock.elapsedTime * 0.8) * 0.08
  })

  return (
    <group
      ref={clusterRef}
      position={[0.55, 0.2, 0.7]}
      rotation={[0.16, 0.2, 0]}
      scale={1.22}
    >
      <mesh>
        <icosahedronGeometry args={[1.25, 0]} />
        <meshBasicMaterial
          color="#617365"
          wireframe
          transparent
          opacity={0.92}
        />
      </mesh>

      {innerPoints.map(([x, y, z, size], index) => (
        <InnerPoint
          key={index}
          index={index}
          position={[x, y, z]}
          size={size}
        />
      ))}
    </group>
  )
}

function VectorSpace() {
  const groupRef = useRef()

  useFrame((state) => {
    if (!groupRef.current) return

    groupRef.current.rotation.y =
      Math.sin(state.clock.elapsedTime * 0.18) * 0.07
  })

  return (
    <group ref={groupRef} rotation={[-0.14, -0.28, 0]}>
      {/* Floor grid */}
      <gridHelper
        args={[5.5, 8, '#b2afa5', '#d8d5cc']}
        position={[0, -1.7, 0]}
      />

      {/* Back grid */}
      <gridHelper
        args={[5.5, 8, '#b2afa5', '#d8d5cc']}
        position={[0, 0.75, -1.95]}
        rotation={[Math.PI / 2, 0, 0]}
      />

      {/* Side grid */}
      <gridHelper
        args={[5.5, 8, '#b2afa5', '#d8d5cc']}
        position={[-2.35, 0.75, 0]}
        rotation={[0, 0, Math.PI / 2]}
      />

      {outerPoints.map(([x, y, z, size], index) => (
        <FloatingPoint
          key={index}
          index={index}
          position={[x, y, z]}
          size={size}
        />
      ))}

      <PolyhedronCluster />
    </group>
  )
}

function CareerScene() {
  return (
    <div className="career-scene">
      <Canvas
        camera={{
          position: [0, 0.2, 6.2],
          fov: 42,
        }}
        gl={{
          alpha: true,
          antialias: true,
        }}
      >
        <ambientLight intensity={1.95} />
        <directionalLight position={[4, 6, 5]} intensity={1.2} />
        <VectorSpace />
      </Canvas>
    </div>
  )
}

export default CareerScene