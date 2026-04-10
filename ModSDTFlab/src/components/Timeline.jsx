import { useState } from 'react'

// Event colors based on type - derived from backend events
const EVENT_COLORS = {
  // Raft events
  election: '#FFB95F',
  'leader_elected': '#FFB95F',
  request_vote: '#89CEFF',
  append_entries: '#4EDEA3',
  commit: '#4EDEA3',
  // Paxos events
  prepare: '#FFB95F',
  promise: '#89CEFF',
  accept: '#89CEFF',
  accepted: '#4EDEA3',
  decision: '#4EDEA3',
  // WAL events
  request_received: '#89CEFF',
  log_append: '#FFB95F',
  log_append_complete: '#FFB95F',
  flush: '#FFB95F',
  flush_complete: '#FFB95F',
  apply: '#4EDEA3',
  apply_complete: '#4EDEA3',
  crash: '#FFB4AB',
  recovery: '#FFB95F',
  recovery_started: '#FFB95F',
  replay_entry: '#4EDEA3',
  skip_entry: '#FFB4AB',
  recovery_completed: '#4EDEA3',
  // Gossip events
  gossip: '#89CEFF',
  gossip_update: '#89CEFF',
  suspicion: '#FFB95F',
  // Transaction events
  tx_prepare: '#FFB95F',
  prepared: '#FFB95F',
  commit_tx: '#4EDEA3',
  abort: '#FFB4AB',
  // Generic states
  start: '#89CEFF',
  sync: '#89CEFF',
  checkpoint: '#BEC8D2',
  idle: '#BEC8D2',
  // Default
  default: '#89CEFF',
}

function getEventColor(type) {
  return EVENT_COLORS[type] || EVENT_COLORS.default
}

export function Timeline({ 
  isPlaying, 
  currentTime, 
  onTimeChange, 
  onPlayPause, 
  onStep,
  events = [],
  stepIndex = 0,
  totalSteps = 0,
}) {
  // Use step-based time when we have execution history
  const isStepBased = totalSteps > 1
  
  // Progress based on steps
  const progress = isStepBased 
    ? (stepIndex / Math.max(1, totalSteps - 1)) * 100 
    : (currentTime / 10) * 100

  return (
    <div className="space-y-3">
      {/* Track */}
      <div className="relative h-8 bg-surface-inset rounded">
        {/* Step markers based on history */}
        {isStepBased ? (
          Array.from({ length: totalSteps }).map((_, i) => (
            <div
              key={i}
              className={`absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full cursor-pointer hover:scale-150 transition-transform ${
                i === stepIndex ? 'ring-2 ring-primary ring-offset-1' : ''
              }`}
              style={{
                left: `${(i / Math.max(1, totalSteps - 1)) * 100}%`,
                backgroundColor: i <= stepIndex ? '#4EDEA3' : '#89CEFF',
                transform: 'translate(-50%, -50%)',
              }}
              title={`Step ${i + 1}/${totalSteps}`}
              onClick={() => onStep && onStep(i - stepIndex)}
            />
          ))
        ) : (
          /* Time-based when no history */
          events.map((event, i) => (
            <div
              key={i}
              className="absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full cursor-pointer hover:scale-150 transition-transform"
              style={{
                left: `${(event.time / 10) * 100}%`,
                backgroundColor: getEventColor(event.type),
                transform: 'translate(-50%, -50%)',
              }}
              title={`${event.time}s: ${event.label || event.type}`}
              onClick={() => onTimeChange(event.time)}
            />
          ))
        )}
        
        {/* Progress bar */}
        <div
          className="absolute top-0 left-0 h-full bg-primary/20 rounded-l transition-all duration-100"
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
        
        {/* Playhead */}
        <div
          className="absolute top-0 w-px h-full bg-primary"
          style={{ left: `${Math.min(progress, 100)}%` }}
        />
      </div>
      
      {/* Controls */}
      <div className="flex items-center gap-3">
        <button
          onClick={onPlayPause}
          className="w-8 h-8 flex items-center justify-center rounded bg-surface-high hover:bg-primary/20 transition-colors"
        >
          {isPlaying ? (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 4h3v12H5V4zm7 0h3v12h-3V4z" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M6 4l10 6-10 6V4z" />
            </svg>
          )}
        </button>
        
        <button
          onClick={() => onStep(-1)}
          className="w-8 h-8 flex items-center justify-center rounded bg-surface-high hover:bg-primary/20 transition-colors"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M12 4l-8 6 8 6V4z" />
          </svg>
        </button>
        
        <button
          onClick={() => onStep(1)}
          className="w-8 h-8 flex items-center justify-center rounded bg-surface-high hover:bg-primary/20 transition-colors"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M8 4l8 6-8 6V4z" />
          </svg>
        </button>
        
        {isStepBased ? (
          <span className="font-mono text-sm text-text-secondary w-24">
            Step {stepIndex + 1} / {totalSteps}
          </span>
        ) : (
          <>
            <input
              type="range"
              min={0}
              max={10}
              step={0.1}
              value={currentTime}
              onChange={(e) => onTimeChange(parseFloat(e.target.value))}
              className="flex-1"
            />
            <span className="font-mono text-sm text-text-secondary w-16 text-right">
              {currentTime.toFixed(1)}s
            </span>
          </>
        )}
      </div>
      
      {/* Event list - show events for current step only */}
      <div className="flex gap-2 overflow-x-auto pb-1 text-xs">
        {totalSteps === 0 ? (
          <span className="text-text-secondary text-sm px-2 py-1">No events yet</span>
        ) : events.length === 0 ? (
          <span className="text-text-secondary text-sm px-2 py-1">Step {stepIndex + 1} - no events</span>
        ) : (
          events.map((event, i) => (
            <span
              key={i}
              className="px-2 py-1 rounded whitespace-nowrap bg-surface-high text-text-primary"
              style={{ borderLeft: `3px solid ${getEventColor(event.type)}` }}
            >
              {event.label || event.type}
            </span>
          ))
        )}
      </div>
    </div>
  )
}

export function useTimeline(isRunning, nodeStates, setNodeStates) {
  const [currentTime, setCurrentTime] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  
  const handlePlayPause = () => setIsPlaying(p => !p)
  const handleStep = (dir) => setCurrentTime(t => Math.max(0, Math.min(10, t + dir)))
  const handleTimeChange = (t) => setCurrentTime(t)
  
  return {
    currentTime,
    isPlaying,
    handlePlayPause,
    handleStep,
    handleTimeChange,
  }
}
