export function TopologyGraph({ topology }) {
  const nodeColors = {
    leader: '#FFB95F',
    follower: '#89CEFF',
  }
  
  return (
    <div className="bg-surface-standard rounded-lg p-4 aspect-[4/3] relative">
      <svg viewBox="0 0 100 100" className="w-full h-full">
        {topology.links.map((link, i) => {
          const src = topology.nodes.find(n => n.id === link.source)
          const tgt = topology.nodes.find(n => n.id === link.target)
          return (
            <line
              key={i}
              x1={src.x}
              y1={src.y}
              x2={tgt.x}
              y2={tgt.y}
              stroke="#89CEFF"
              strokeWidth="0.5"
              strokeOpacity="0.3"
            />
          )
        })}
        {topology.nodes.map((node) => (
          <g key={node.id}>
            <circle
              cx={node.x}
              cy={node.y}
              r="6"
              fill={nodeColors[node.type]}
              stroke="#0B1326"
              strokeWidth="1"
            />
            <text
              x={node.x}
              y={node.y + 10}
              textAnchor="middle"
              className="text-[4px] fill-text-secondary font-mono"
            >
              {node.id}
            </text>
          </g>
        ))}
      </svg>
    </div>
  )
}