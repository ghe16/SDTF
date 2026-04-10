import { useMemo } from 'react'

const NODE_STATE_CONFIGS = {
  // Raft-style (leader-based)
  raft: {
    states: {
      leader: { color: '#FFB95F', label: 'LEADER' },
      candidate: { color: '#89CEFF', label: 'CANDIDATE' },
      follower: { color: '#4EDEA3', label: 'FOLLOWER' },
      crashed: { color: '#FFB4AB', label: 'CRASHED' },
    },
    defaultState: 'follower',
  },
  // Paxos-style (proposer/acceptor)
  paxos: {
    states: {
      proposer: { color: '#FFB95F', label: 'PROPOSER' },
      acceptor: { color: '#4EDEA3', label: 'ACCEPTOR' },
      learner: { color: '#89CEFF', label: 'LEARNER' },
      preparing: { color: '#FFB95F', label: 'PREPARING' },
      promising: { color: '#89CEFF', label: 'PROMISING' },
      accepting: { color: '#89CEFF', label: 'ACCEPTING' },
      decided: { color: '#4EDEA3', label: 'DECIDED' },
      crashed: { color: '#FFB4AB', label: 'CRASHED' },
    },
    defaultState: 'acceptor',
  },
  // WAL/Pipeline
  wal: {
    states: {
      idle: { color: '#4EDEA3', label: 'IDLE' },
      ready: { color: '#4EDEA3', label: 'READY' },
      requesting: { color: '#89CEFF', label: 'REQUESTING' },
      appending: { color: '#FFB95F', label: 'APPENDDING' },
      flushing: { color: '#FFB95F', label: 'FLUSHING' },
      applying: { color: '#89CEFF', label: 'APPLYING' },
      recovering: { color: '#FFB95F', label: 'RECOVERING' },
      crashed: { color: '#FFB4AB', label: 'CRASHED' },
    },
    defaultState: 'idle',
  },
  // Gossip
  gossip: {
    states: {
      active: { color: '#4EDEA3', label: 'ACTIVE' },
      suspect: { color: '#FFB95F', label: 'SUSPECT' },
      dead: { color: '#FFB4AB', label: 'DEAD' },
      updating: { color: '#89CEFF', label: 'UPDATING' },
    },
    defaultState: 'active',
  },
  // Transaction (2PC)
  transaction: {
    states: {
      coordinator: { color: '#FFB95F', label: 'COORDINATOR' },
      participant: { color: '#89CEFF', label: 'PARTICIPANT' },
      aborted: { color: '#FFB4AB', label: 'ABORTED' },
      committed: { color: '#4EDEA3', label: 'COMMITTED' },
      voting: { color: '#89CEFF', label: 'VOTING' },
      prepared: { color: '#FFB95F', label: 'PREPARED' },
    },
    defaultState: 'participant',
  },
  // CRDT
  crdt: {
    states: {
      active: { color: '#4EDEA3', label: 'ACTIVE' },
      merging: { color: '#89CEFF', label: 'MERGING' },
      syncing: { color: '#FFB95F', label: 'SYNCING' },
    },
    defaultState: 'active',
  },
  // Generic fallback
  default: {
    states: {
      default: { color: '#89CEFF', label: 'NODE' },
      crashed: { color: '#FFB4AB', label: 'CRASHED' },
    },
    defaultState: 'default',
  },
}

const LAYOUT_MODES = {
  cluster: { type: 'circular', radius: 35 },
  'paxos-cluster': { type: 'paxos', radius: 35 },
  pipeline: { type: 'linear' },
  mesh: { type: 'grid' },
}

export function GraphVisualization({ 
  nodeStates = {}, 
  onNodeClick,
  nodes = [],    
  edges = [],   
  layoutType = 'cluster',
  messages = [],
  algorithmType = 'default',
}) {
  const layout = LAYOUT_MODES[layoutType] || LAYOUT_MODES.cluster
  const stateConfig = NODE_STATE_CONFIGS[algorithmType] || NODE_STATE_CONFIGS.default
  
  const getNodeState = (state) => {
    return stateConfig.states[state] || stateConfig.states[stateConfig.defaultState] || { color: '#89CEFF', label: 'NODE' }
  }
  
  const graphData = useMemo(() => {
    // Use backend-provided nodes and edges if available
    if (nodes.length > 0) {
      const nodePositions = {}
      
      if (layout.type === 'linear') {
        // Pipeline layout: linear left to right
        const spacing = 80 / (nodes.length + 1)
        nodes.forEach((node, i) => {
          nodePositions[node.id] = {
            x: spacing * (i + 1) + 10,
            y: 50,
          }
        })
      } else if (layout.type === 'circular') {
        // Cluster layout: circular (Raft-style)
        const count = nodes.length
        nodes.forEach((node, i) => {
          const angle = (2 * Math.PI * i / count) - Math.PI / 2
          nodePositions[node.id] = {
            x: 50 + layout.radius * Math.cos(angle),
            y: 50 + layout.radius * Math.sin(angle),
          }
        })
      } else if (layout.type === 'paxos') {
        // Paxos cluster: neutral distributed ring (no leader emphasis)
        const count = nodes.length
        nodes.forEach((node, i) => {
          const angle = (2 * Math.PI * i / count) - Math.PI / 2
          nodePositions[node.id] = {
            x: 50 + layout.radius * Math.cos(angle),
            y: 50 + layout.radius * Math.sin(angle),
          }
        })
      } else {
        // Grid layout for mesh
        const cols = Math.ceil(Math.sqrt(nodes.length))
        nodes.forEach((node, i) => {
          nodePositions[node.id] = {
            x: 20 + (i % cols) * 25 + 10,
            y: 20 + Math.floor(i / cols) * 25,
          }
        })
      }
      
      return {
        nodes: nodes.map((n) => ({
          ...n,
          x: nodePositions[n.id]?.x ?? 50,
          y: nodePositions[n.id]?.y ?? 50,
          state: nodeStates[n.id] || n.state || 'default',
        })),
        links: edges.map(e => ({
          from: e.from || e.source,
          to: e.to || e.target,
        })),
      }
    }
    
    // No backend data - return empty graph
    return { nodes: [], links: [] }
  }, [nodes, edges, nodeStates, layout])
  
  const { nodes: graphNodes, links: graphLinks } = graphData
  
  return (
    <div className="relative w-full aspect-square max-w-sm mx-auto">
      <svg viewBox="0 0 100 100" className="w-full h-full">
        {/* Edges */}
        {graphLinks.map((link, i) => {
          const from = graphNodes.find(n => n.id === link.from)
          const to = graphNodes.find(n => n.id === link.to)
          if (!from || !to) return null
          return (
            <line
              key={i}
              x1={from.x}
              y1={from.y}
              x2={to.x}
              y2={to.y}
              stroke="#89CEFF"
              strokeWidth="0.5"
              strokeOpacity="0.3"
            />
          )
        })}
        
        {/* Animated Messages */}
        {messages.map((msg, i) => {
          const from = graphNodes.find(n => n.id === msg.from)
          const to = graphNodes.find(n => n.id === msg.to)
          if (!from || !to) return null
          
          const color = msg.type === 'prepare' ? '#FFB95F' : 
                        msg.type === 'promise' ? '#4EDEA3' : 
                        msg.type === 'accept' ? '#89CEFF' : '#89CEFF'
          
          // Calculate midpoint
          const midX = (from.x + to.x) / 2
          const midY = (from.y + to.y) / 2
          
          return (
            <circle
              key={`msg-${i}`}
              cx={midX}
              cy={midY}
              r="2.5"
              fill={color}
              className="animate-pulse"
            />
          )
        })}
        
        {/* Nodes */}
        {graphNodes.map(node => {
          const state = getNodeState(node.state)
          return (
            <g
              key={node.id}
              onClick={() => onNodeClick?.(node.id)}
              className="cursor-pointer"
            >
              {/* Outer ring */}
              <circle
                cx={node.x}
                cy={node.y}
                r="8"
                fill="none"
                stroke={state.color}
                strokeWidth="0.5"
                strokeOpacity="0.3"
              />
              {/* Inner node */}
              <circle
                cx={node.x}
                cy={node.y}
                r="5"
                fill={state.color}
                className={node.state === 'crashed' ? 'animate-pulse' : ''}
              />
              {/* Label */}
              <text
                x={node.x}
                y={node.y + 12}
                textAnchor="middle"
                className="text-[3.5px] fill-text-secondary font-mono"
              >
                {node.id}
              </text>
              {/* State label */}
              {state.label && (
                <text
                  x={node.x}
                  y={node.y - 10}
                  textAnchor="middle"
                  className="text-[2.5px] fill-text-secondary font-mono"
                >
                  {state.label}
                </text>
              )}
            </g>
          )
        })}
      </svg>
    </div>
  )
}
