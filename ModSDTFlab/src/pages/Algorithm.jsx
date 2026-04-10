import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Card } from '../components/Card'
import { Button } from '../components/Button'
import { StatusChip } from '../components/StatusChip'
import { LogMatrix } from '../components/LogMatrix'
import { GraphVisualization } from '../components/GraphVisualization'
import { Timeline } from '../components/Timeline'
import { ValidationPanel } from '../components/ValidationPanel'
import { api } from '../api/client'
import { getProfile } from '../config/algorithmProfiles'

export default function Algorithm() {
  const [searchParams] = useSearchParams()
  const algoId = searchParams.get('algo') || 'paxos'
  
  const [algorithm, setAlgorithm] = useState(null)
  const [executionId, setExecutionId] = useState(null)
  const [isRunning, setIsRunning] = useState(false)
  const [nodeCount, setNodeCount] = useState(5)
  const [scenario, setScenario] = useState('normal_write')
  const [faultTolerance, setFaultTolerance] = useState(1)
  const [candidates, setCandidates] = useState(1)
  const [terms, setTerms] = useState(1)
  const [proposerCount, setProposerCount] = useState(1)
  const [proposalRounds, setProposalRounds] = useState(1)
  const [messageDelay, setMessageDelay] = useState(50)
  const [heartbeatTimeout, setHeartbeatTimeout] = useState(150)
  const [electionTimeout, setElectionTimeout] = useState(200)
  const [batchSize, setBatchSize] = useState(1)
  const [flushDelay, setFlushDelay] = useState(10)
  const [crashMode, setCrashMode] = useState('none')
  const [fanout, setFanout] = useState(3)
  const [gossipInterval, setGossipInterval] = useState(100)
  const [timeout, setTimeout] = useState(5000)
  const [retries, setRetries] = useState(3)
  const [crashProbability, setCrashProbability] = useState(0)
  const [mergeStrategy, setMergeStrategy] = useState('lww')
  const [nodeStates, setNodeStates] = useState({})
  const [currentTime, setCurrentTime] = useState(0)
  const [logs, setLogs] = useState([])
  const [result, setResult] = useState(null)
  const [validationData, setValidationData] = useState(null)
  const [stateData, setStateData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [debugInfo, setDebugInfo] = useState(null)
  const [showDebug, setShowDebug] = useState(false)
  
  // Execution history for timeline interaction
  const [executionHistory, setExecutionHistory] = useState([])
  const [selectedStep, setSelectedStep] = useState(0)
  
  // Keep nodeStates synced with stateData
  useEffect(() => {
    if (stateData?.graph?.node_states) {
      setNodeStates(stateData.graph.node_states)
    }
  }, [stateData])
  
  // Load algorithm on mount - with fallback
  useEffect(() => {
    console.log('Loading algorithm:', algoId)
    api.getAlgorithm(algoId)
      .then(data => {
        console.log('Algorithm loaded:', data)
        if (data && data.name) {
          setAlgorithm(data)
        } else {
          // API returned but no valid data - use fallback
          setAlgorithm({ id: algoId, name: algoId.toUpperCase(), description: '' })
        }
      })
      .catch(err => {
        console.error('Failed to load algorithm:', err)
        // Always set a fallback so page renders
        setAlgorithm({ id: algoId, name: algoId.toUpperCase(), description: '' })
      })
  }, [algoId])
  
  // Get UI profile based on algorithm type - always available
  const uiProfile = getProfile(algoId)
  
  // Start execution and run to completion
  const handleRun = async () => {
    if (executionId) {
      setIsRunning(false)
      setExecutionId(null)
      setCurrentTime(0)
      setResult(null)
      setLogs([])
      return
    }
    
    try {
      setIsLoading(true)
      setDebugInfo(null)
      
      let execConfig = {}
      let execScenario = null
      
      // Build config based on uiProfile parameters
      if (uiProfile.configParams.includes('scenario')) {
        execScenario = scenario
      }
      
      // Collect all relevant config params
      if (uiProfile.configParams.includes('faultTolerance')) {
        execConfig.fault_tolerance = faultTolerance
      }
      if (uiProfile.configParams.includes('candidates')) {
        execConfig.num_candidates = candidates
      }
      if (uiProfile.configParams.includes('terms')) {
        execConfig.num_terms = terms
      }
      if (uiProfile.configParams.includes('proposerCount')) {
        execConfig.proposer_count = proposerCount
      }
      if (uiProfile.configParams.includes('proposalRounds')) {
        execConfig.proposal_rounds = proposalRounds
      }
      if (uiProfile.configParams.includes('messageDelay')) {
        execConfig.message_delay = messageDelay
      }
      if (uiProfile.configParams.includes('heartbeatTimeout')) {
        execConfig.heartbeat_timeout = heartbeatTimeout
      }
      if (uiProfile.configParams.includes('electionTimeout')) {
        execConfig.election_timeout = electionTimeout
      }
      if (uiProfile.configParams.includes('batchSize')) {
        execConfig.batch_size = batchSize
      }
      if (uiProfile.configParams.includes('flushDelay')) {
        execConfig.flush_delay = flushDelay
      }
      if (uiProfile.configParams.includes('crashMode')) {
        execConfig.crash_mode = crashMode
      }
      if (uiProfile.configParams.includes('fanout')) {
        execConfig.fanout = fanout
      }
      if (uiProfile.configParams.includes('interval')) {
        execConfig.gossip_interval = gossipInterval
      }
      if (uiProfile.configParams.includes('timeout')) {
        execConfig.timeout = timeout
      }
      if (uiProfile.configParams.includes('retries')) {
        execConfig.retries = retries
      }
      if (uiProfile.configParams.includes('mergeStrategy')) {
        execConfig.merge_strategy = mergeStrategy
      }
      if (uiProfile.configParams.includes('crashProbability')) {
        execConfig.crash_probability = crashProbability
      }
      if (uiProfile.configParams.includes('nodes')) {
        execConfig.node_count = nodeCount
      }
      
      const startRes = await api.startExecution(algoId, nodeCount, execConfig, execScenario)
      setExecutionId(startRes.id)
      setIsRunning(true)
      setCurrentTime(0)
      setResult(null)
      setValidationData(null)
      setStateData(null)
      setLogs([])
      setExecutionHistory([])
      setSelectedStep(0)
      
      // Run to completion and capture history
      const runRes = await api.runExecution(startRes.id)
      
      // Use history from backend or create from final state
      if (runRes.history && runRes.history.length > 0) {
        setExecutionHistory(runRes.history)
        
        // Initialize at step 0
        setSelectedStep(0)
        updateDisplayFromStep(0)
      } else {
        // Fallback: get final state
        const [state, logsRes, resultRes, validationRes] = await Promise.all([
          api.getExecutionState(startRes.id),
          api.getExecutionLogs(startRes.id),
          api.getExecutionResult(startRes.id),
          api.getExecutionValidation(startRes.id),
        ])
        setStateData(state)
        setLogs(state.logs || logsRes.logs || [])
        setExecutionHistory([state])
        setSelectedStep(0)
        setNodeStates(state.graph?.node_states || state.node_states || {})
        setCurrentTime(state.current_time || 0)
        
        if (resultRes.result) {
          setResult(resultRes.result)
        } else if (state.result) {
          setResult(state.result)
        }
        
        if (validationRes.validation) {
          setValidationData(validationRes.validation)
        } else if (state.validation) {
          setValidationData(state.validation)
        }
      }
      
      setIsRunning(false)
      setIsLoading(false)
    } catch (err) {
      console.error('Failed to run:', err)
      setIsRunning(false)
      setIsLoading(false)
    }
  }
  
  // Sync timeline with backend time
  const handlePlayPause = () => {
    // Just toggle local playback - backend doesn't control this yet
    setIsRunning(!isRunning)
  }
  
  const handleStep = (dir) => {
    // Navigate through execution history steps directly
    const maxStep = executionHistory.length - 1
    const newStep = Math.max(0, Math.min(maxStep, selectedStep + dir))
    setSelectedStep(newStep)
    updateDisplayFromStep(newStep)
  }
  
  const handleTimeChange = (t) => {
    // Convert slider position to step index - use step index as time reference
    const maxStep = executionHistory.length - 1
    if (maxStep >= 0) {
      const stepIndex = Math.min(maxStep, Math.floor(t))
      setSelectedStep(stepIndex)
      updateDisplayFromStep(stepIndex)
    }
  }
  
  // Get logs for current step only (not cumulative)
  const getLogsForStep = (stepIndex) => {
    if (executionHistory.length === 0 || stepIndex >= executionHistory.length) return []
    const stepData = executionHistory[stepIndex]
    return stepData?.logs || []
  }
  
  // Get events for current step only (not cumulative)
  const getEventsForStep = (stepIndex) => {
    if (executionHistory.length === 0 || stepIndex >= executionHistory.length) return []
    const stepData = executionHistory[stepIndex]
    return stepData?.events || []
  }
  
  const updateDisplayFromStep = (stepIndex) => {
    if (executionHistory.length === 0 || stepIndex >= executionHistory.length) return
    
    const stepData = executionHistory[stepIndex]
    if (!stepData) return
    
    // Sync all three: graph state, logs, and time reference
    setStateData({...stepData})
    setNodeStates(stepData.graph?.node_states || stepData.node_states || {})
    setCurrentTime(stepIndex)
    
    // Show logs for THIS step only
    const stepLogs = getLogsForStep(stepIndex)
    setLogs(stepLogs)
  }
  
  if (!algorithm) {
    return <div className="p-8 text-text-secondary">Loading...</div>
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold tracking-tight">{algorithm.name}</h1>
          <StatusChip status={isLoading ? 'loading' : (executionId ? 'active' : 'inactive')} />
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowDebug(d => !d)}
            className="px-3 py-1.5 text-xs text-text-secondary hover:text-text-primary border border-surface-high rounded hover:bg-surface-high transition-colors"
          >
            {showDebug ? 'Hide Debug' : 'Debug'}
          </button>
          <Button onClick={handleRun} disabled={isLoading}>
            {isLoading ? 'Loading...' : (executionId ? 'Stop' : 'Run')}
          </Button>
        </div>
      </div>
      
      {/* Debug Panel */}
      {showDebug && debugInfo && (
        <Card className="bg-surface-inset">
          <div className="space-y-2 text-xs font-mono">
            <div className="flex items-center gap-2">
              <span className="text-text-secondary">Execution:</span>
              <span className="text-primary">{debugInfo.executionId}</span>
              <span className="text-text-secondary">| Algorithm:</span>
              <span className="text-secondary">{debugInfo.algorithm}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-text-secondary">Graph:</span>
              <span className={(debugInfo.state?.graph?.nodes?.length || 0) > 0 ? 'text-secondary' : 'text-error'}>
                {debugInfo.state?.graph?.nodes?.length || 0} nodes, {debugInfo.state?.graph?.edges?.length || 0} edges
              </span>
              {(debugInfo.state?.graph?.nodes?.length || 0) === 0 && (
                <span className="text-error text-xs">⚠ Empty graph data!</span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-text-secondary">Events:</span>
              <span className={(debugInfo.state?.events?.length || 0) > 0 ? 'text-secondary' : 'text-error'}>
                {debugInfo.state?.events?.length || 0} events
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-text-secondary">Logs:</span>
              <span className="text-text-primary">{debugInfo.logs?.length || 0} entries</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-text-secondary">Result:</span>
              <span className="text-text-primary">
                {debugInfo.result ? Object.keys(debugInfo.result).join(', ') : 'none'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-text-secondary">Validation:</span>
              <span className={debugInfo.validation?.success ? 'text-secondary' : 'text-error'}>
                {debugInfo.validation ? (debugInfo.validation.success ? 'PASSED' : 'FAILED') : 'none'}
              </span>
            </div>
          </div>
        </Card>
      )}
      
      {/* Warning for empty graph */}
      {debugInfo && (debugInfo.state?.graph?.nodes?.length || 0) === 0 && (
        <div className="bg-error/10 border border-error/30 rounded px-4 py-2 text-sm text-error">
          ⚠ Backend returned empty graph data. Check backend logs or algorithm implementation.
        </div>
      )}
      
      {/* Main Grid */}
      <div className="grid lg:grid-cols-4 gap-6">
        {/* Left: Dynamic Config */}
        <div className="lg:col-span-1 space-y-4">
          {/* Algorithm-specific config fields */}
          <Card>
            <h3 className="text-sm font-medium text-text-secondary mb-4">Configuration</h3>
            <div className="space-y-4">
              {/* Node Count - most algorithms */}
              {uiProfile.configParams.includes('nodes') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Node Count</label>
                  <input
                    type="number"
                    value={nodeCount}
                    onChange={(e) => setNodeCount(Math.max(2, Math.min(10, parseInt(e.target.value) || 3)))}
                    min={2}
                    max={10}
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                  />
                </div>
              )}
              
              {/* Scenario - WAL */}
              {uiProfile.configParams.includes('scenario') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Scenario</label>
                  <select 
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                    onChange={(e) => setScenario(e.target.value)}
                    value={scenario}
                  >
                    <option value="normal_write">Normal Write</option>
                    <option value="crash_after_log">Crash After Log</option>
                    <option value="multiple_operations">Multiple Operations</option>
                    <option value="crash_after_first">Crash After First</option>
                  </select>
                </div>
              )}
              
              {/* Batch Size - WAL */}
              {uiProfile.configParams.includes('batchSize') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Batch Size</label>
                  <input
                    type="number"
                    value={batchSize}
                    onChange={(e) => setBatchSize(Math.max(1, parseInt(e.target.value) || 1))}
                    min={1}
                    max={100}
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                  />
                </div>
              )}
              
              {/* Flush Delay - WAL */}
              {uiProfile.configParams.includes('flushDelay') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Flush Delay (ms)</label>
                  <input
                    type="number"
                    value={flushDelay}
                    onChange={(e) => setFlushDelay(Math.max(0, parseInt(e.target.value) || 10))}
                    min={0}
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                  />
                </div>
              )}
              
              {/* Crash Mode - WAL */}
              {uiProfile.configParams.includes('crashMode') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Crash Mode</label>
                  <select 
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                    value={crashMode}
                    onChange={(e) => setCrashMode(e.target.value)}
                  >
                    <option value="none">None</option>
                    <option value="after_append">After Append</option>
                    <option value="after_flush">After Flush</option>
                    <option value="random">Random</option>
                  </select>
                </div>
              )}
              
              {/* Fault Tolerance - consensus */}
              {uiProfile.configParams.includes('faultTolerance') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Fault Tolerance</label>
                  <select 
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                    value={faultTolerance}
                    onChange={(e) => setFaultTolerance(parseInt(e.target.value))}
                  >
                    <option value={1}>1 node</option>
                    <option value={2}>2 nodes</option>
                    <option value={3}>3 nodes</option>
                  </select>
                </div>
              )}
              
              {/* Candidates - Raft */}
              {uiProfile.configParams.includes('candidates') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Candidates</label>
                  <select 
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                    value={candidates}
                    onChange={(e) => setCandidates(parseInt(e.target.value))}
                  >
                    <option value={1}>1 candidate</option>
                    <option value={2}>2 candidates</option>
                    <option value={3}>3 candidates</option>
                  </select>
                </div>
              )}
              
              {/* Terms - Raft */}
              {uiProfile.configParams.includes('terms') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Terms</label>
                  <select 
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                    value={terms}
                    onChange={(e) => setTerms(parseInt(e.target.value))}
                  >
                    <option value={1}>1 term</option>
                    <option value={2}>2 terms</option>
                    <option value={3}>3 terms</option>
                  </select>
                </div>
              )}
              
              {/* Proposer Count - Paxos */}
              {uiProfile.configParams.includes('proposerCount') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Proposers</label>
                  <select 
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                    value={proposerCount}
                    onChange={(e) => setProposerCount(parseInt(e.target.value))}
                  >
                    <option value={1}>1 proposer</option>
                    <option value={2}>2 proposers</option>
                    <option value={3}>3 proposers</option>
                  </select>
                </div>
              )}
              
              {/* Proposal Rounds - Paxos */}
              {uiProfile.configParams.includes('proposalRounds') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Proposal Rounds</label>
                  <select 
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                    value={proposalRounds}
                    onChange={(e) => setProposalRounds(parseInt(e.target.value))}
                  >
                    <option value={1}>1 round</option>
                    <option value={2}>2 rounds</option>
                    <option value={3}>3 rounds</option>
                  </select>
                </div>
              )}
              
              {/* Message Delay - consensus */}
              {uiProfile.configParams.includes('messageDelay') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Message Delay (ms)</label>
                  <input
                    type="range"
                    min="0"
                    max="500"
                    value={messageDelay}
                    onChange={(e) => setMessageDelay(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <span className="text-xs text-text-secondary">{messageDelay}ms</span>
                </div>
              )}
              
              {/* Heartbeat Timeout - Raft */}
              {uiProfile.configParams.includes('heartbeatTimeout') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Heartbeat Timeout (ms)</label>
                  <input
                    type="range"
                    min="50"
                    max="500"
                    value={heartbeatTimeout}
                    onChange={(e) => setHeartbeatTimeout(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <span className="text-xs text-text-secondary">{heartbeatTimeout}ms</span>
                </div>
              )}
              
              {/* Election Timeout - consensus */}
              {uiProfile.configParams.includes('electionTimeout') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Election Timeout (ms)</label>
                  <input
                    type="range"
                    min="100"
                    max="1000"
                    value={electionTimeout}
                    onChange={(e) => setElectionTimeout(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <span className="text-xs text-text-secondary">{electionTimeout}ms</span>
                </div>
              )}
              
              {/* Fanout - Gossip */}
              {uiProfile.configParams.includes('fanout') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Fanout</label>
                  <input
                    type="number"
                    value={fanout}
                    onChange={(e) => setFanout(Math.max(1, parseInt(e.target.value) || 3))}
                    min={1}
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                  />
                </div>
              )}
              
              {/* Gossip Interval - Gossip */}
              {uiProfile.configParams.includes('interval') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Gossip Interval (ms)</label>
                  <input
                    type="range"
                    min="50"
                    max="500"
                    value={gossipInterval}
                    onChange={(e) => setGossipInterval(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <span className="text-xs text-text-secondary">{gossipInterval}ms</span>
                </div>
              )}
              
              {/* Timeout - Transaction */}
              {uiProfile.configParams.includes('timeout') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Timeout (ms)</label>
                  <input
                    type="number"
                    value={timeout}
                    onChange={(e) => setTimeout(Math.max(1000, parseInt(e.target.value) || 5000))}
                    min={1000}
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                  />
                </div>
              )}
              
              {/* Retries - Transaction */}
              {uiProfile.configParams.includes('retries') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Retries</label>
                  <input
                    type="number"
                    value={retries}
                    onChange={(e) => setRetries(Math.max(0, parseInt(e.target.value) || 3))}
                    min={0}
                    max={10}
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                  />
                </div>
              )}
               
              {/* Crash Probability - Raft/Paxos */}
              {uiProfile.configParams.includes('crashProbability') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Crash Probability (%)</label>
                  <input
                    type="range"
                    min="0"
                    max="50"
                    value={crashProbability}
                    onChange={(e) => setCrashProbability(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <span className="text-xs text-text-secondary">{crashProbability}%</span>
                </div>
              )}
               
              {/* Merge Strategy - CRDT */}
              {uiProfile.configParams.includes('mergeStrategy') && (
                <div>
                  <label className="text-xs text-text-secondary block mb-1">Merge Strategy</label>
                  <select 
                    className="w-full bg-surface-low border-none rounded px-3 py-2 text-sm"
                    value={mergeStrategy}
                    onChange={(e) => setMergeStrategy(e.target.value)}
                  >
                    <option value="lww">LWW (Last-Write-Wins)</option>
                    <option value="gcounter">GCounter</option>
                    <option value="pncounter">PN-Counter</option>
                    <option value="orset">OR-Set</option>
                  </select>
                </div>
              )}
              
              {/* Algorithm Type Badge */}
              <div className="pt-2 border-t border-surface-high">
                <span className="text-xs text-text-secondary">Type: </span>
                <span className="text-xs font-medium text-primary capitalize">{uiProfile.category || uiProfile.type}</span>
              </div>
            </div>
            </Card>
        </div>
        
        {/* Center: Graph + Timeline */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-text-secondary">Graph Visualization</h3>
              <span className="text-xs text-text-secondary">{uiProfile.nodeLabel}s</span>
            </div>
            <GraphVisualization
              nodeStates={stateData?.graph?.node_states || {}}
              nodes={stateData?.graph?.nodes || []}
              edges={stateData?.graph?.edges || []}
              layoutType={uiProfile.graphType}
              algorithmType={uiProfile.category || 'default'}
              messages={stateData?.metadata?.messages || []}
              onNodeClick={(id) => {
                // Generic toggle - works for most algorithms
                setNodeStates(prev => ({
                  ...prev,
                  [id]: prev[id] === 'crashed' ? 'default' : 'crashed'
                }))
              }}
            />
          </Card>
          
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-text-secondary">Timeline</h3>
              <span className="text-xs text-text-secondary">{uiProfile.timelineLabel || 'Events'}</span>
            </div>
            <Timeline
              isPlaying={isRunning}
              currentTime={selectedStep}
              onTimeChange={handleTimeChange}
              onPlayPause={handlePlayPause}
              onStep={handleStep}
              events={getEventsForStep(selectedStep)}
              stepIndex={selectedStep}
              totalSteps={executionHistory.length}
            />
          </Card>
        </div>
        
        {/* Right: Logs + Results */}
        <div className="lg:col-span-1 space-y-6">
          <Card glass>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-text-secondary">Logs</h3>
              <span className={`flex items-center gap-2 text-xs ${isRunning ? 'text-secondary' : 'text-text-secondary'}`}>
                <span className={`w-2 h-2 rounded-full ${isRunning ? 'bg-secondary animate-pulse' : 'bg-surface-high'}`}></span>
                {isRunning ? 'Live' : 'Idle'}
              </span>
            </div>
            <LogMatrix 
              logs={logs.length > 0 ? logs : []} 
              highlightIndex={executionHistory.length > 0 && selectedStep > 0 ? Math.min(selectedStep - 1, logs.length - 1) : -1}
            />
          </Card>
          
          <Card>
            <h3 className="text-sm font-medium text-text-secondary mb-4">Results</h3>
            {!result || Object.keys(result).length === 0 ? (
              <div className="text-center py-6 text-text-secondary text-sm">
                {isRunning ? 'Running...' : 'No results yet'}
              </div>
            ) : (
              <div className="space-y-3">
                {(() => {
                  // Sort entries: metricParams first (in order), then others alphabetically
                  const metricOrder = uiProfile.metricParams || []
                  const entries = Object.entries(result).sort(([a], [b]) => {
                    const aIdx = metricOrder.indexOf(a)
                    const bIdx = metricOrder.indexOf(b)
                    if (aIdx >= 0 && bIdx >= 0) return aIdx - bIdx
                    if (aIdx >= 0) return -1
                    if (bIdx >= 0) return 1
                    return a.localeCompare(b)
                  })
                  return entries.map(([key, value]) => {
                    const label = key
                      .replace(/_/g, ' ')
                      .replace(/(\w)([A-Z])/g, '$1 $2')
                      .toLowerCase()
                      .replace(/^./, str => str.toUpperCase())
                    
                    let displayValue = value
                    if (typeof value === 'boolean') {
                      displayValue = value ? '✓' : '✗'
                    } else if (typeof value === 'number') {
                      displayValue = value.toLocaleString()
                    }
                    
                    return (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-text-secondary">{label}</span>
                        <span className="font-mono text-text-primary">{displayValue}</span>
                      </div>
                    )
                  })
                })()}
              </div>
            )}
          </Card>
          
          <ValidationPanel validation={validationData} isRunning={isRunning} />
        </div>
      </div>
    </div>
  )
}