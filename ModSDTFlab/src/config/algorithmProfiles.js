export const algorithmUIProfiles = {
  // Raft-style consensus (leader-based)
  raft: {
    type: 'consensus',
    category: 'raft',
    label: 'Raft',
    graphType: 'cluster',
    nodeLabel: 'Server',
    edgeLabel: 'Replication',
    showRoles: true,
    roles: ['leader', 'candidate', 'follower'],
    configParams: ['nodes', 'faultTolerance', 'candidates', 'terms', 'messageDelay', 'heartbeatTimeout', 'crashProbability', 'retries'],
    metricParams: ['commits', 'leader', 'term', 'logLength'],
    timelineLabel: 'Election & Replication',
    showTimeline: true,
  },
  
  // Paxos-style consensus (proposer-based)
  paxos: {
    type: 'consensus',
    category: 'paxos',
    label: 'Paxos',
    graphType: 'paxos-cluster',
    nodeLabel: 'Acceptor',
    edgeLabel: 'Quorum',
    showRoles: true,
    roles: ['proposer', 'acceptor', 'learner'],
    configParams: ['nodes', 'faultTolerance', 'proposerCount', 'messageDelay', 'proposalRounds', 'crashProbability', 'retries'],
    metricParams: ['proposals', 'promises', 'accepts', 'decisions'],
    timelineLabel: 'Consensus Phases',
    showTimeline: true,
  },
  
  // General consensus (fallback for etcd, leader-election)
  consensus: {
    type: 'consensus',
    category: 'consensus',
    label: 'Consensus',
    graphType: 'cluster',
    nodeLabel: 'Node',
    edgeLabel: 'Communication',
    showRoles: true,
    roles: ['leader', 'candidate', 'follower'],
    configParams: ['nodes', 'faultTolerance', 'messageDelay', 'electionTimeout'],
    metricParams: ['quorumSize', 'decisions', 'rounds'],
    timelineLabel: 'Protocol Events',
    showTimeline: true,
  },
  
  // WAL-based algorithms
  wal: {
    type: 'logging',
    category: 'wal',
    label: 'Write-Ahead Logging',
    graphType: 'pipeline',
    nodeLabel: 'Component',
    edgeLabel: 'Data Flow',
    showRoles: false,
    roles: ['idle', 'ready', 'requesting', 'appending', 'flushing', 'applying', 'recovering', 'crashed'],
    configParams: ['scenario', 'batchSize', 'flushDelay', 'crashMode'],
    metricParams: ['operations', 'logEntries', 'flushes', 'recoveries'],
    timelineLabel: 'Write-Ahead Lifecycle',
    showTimeline: true,
  },
  
  // Gossip/Epidemic protocols
  gossip: {
    type: 'dissemination',
    category: 'gossip',
    label: 'Gossip Protocol',
    graphType: 'mesh',
    nodeLabel: 'Peer',
    edgeLabel: 'Gossip',
    showRoles: false,
    roles: ['active', 'suspect', 'dead'],
    configParams: ['fanout', 'interval', 'cleanupInterval', 'maxPropagationDelay'],
    metricParams: ['peers', 'rounds', 'convergence'],
    timelineLabel: 'Propagation',
    showTimeline: true,
  },
  
  // 2PC/3PC transaction protocols
  transaction: {
    type: 'transaction',
    category: 'transaction',
    label: 'Two-Phase Commit',
    graphType: 'cluster',
    nodeLabel: 'Participant',
    edgeLabel: 'Vote',
    showRoles: true,
    roles: ['coordinator', 'participant', 'aborted', 'committed'],
    configParams: ['timeout', 'retries', 'coordinatorSelection'],
    metricParams: ['participants', 'votes', 'decisions'],
    timelineLabel: 'Transaction Phases',
    showTimeline: true,
  },
  
  // CRDT
  crdt: {
    type: 'replication',
    category: 'crdt',
    label: 'CRDT',
    graphType: 'mesh',
    nodeLabel: 'Replica',
    edgeLabel: 'Sync',
    showRoles: false,
    roles: ['active', 'merging'],
    configParams: ['mergeStrategy', 'gcInterval', 'syncInterval'],
    metricParams: ['replicas', 'merges', 'clocks'],
    timelineLabel: 'Merge Events',
    showTimeline: true,
  },
}

export const defaultProfile = {
  type: 'generic',
  category: 'generic',
  label: 'Generic Algorithm',
  graphType: 'cluster',
  nodeLabel: 'Node',
  edgeLabel: 'Link',
  showRoles: false,
  roles: ['default'],
  configParams: ['nodes'],
  metricParams: ['steps'],
  timelineLabel: 'Execution',
  showTimeline: true,
}

export function getProfile(algorithmId) {
  // Direct algorithm ID mapping to specific profile
  const directMapping = {
    'raft': algorithmUIProfiles.raft,
    'paxos': algorithmUIProfiles.paxos,
    'wal': algorithmUIProfiles.wal,
    'gossip': algorithmUIProfiles.gossip,
    '2pc': algorithmUIProfiles.transaction,
    '3pc': algorithmUIProfiles.transaction,
    'crdt': algorithmUIProfiles.crdt,
  }
  
  if (directMapping[algorithmId]) {
    return directMapping[algorithmId]
  }
  
  // Fallback for unknown consensus-like algorithms
  const consensusFallback = ['etcd', 'leader-election', 'basic-paxos', 'multi-paxos']
  if (consensusFallback.includes(algorithmId)) {
    return algorithmUIProfiles.consensus
  }
  
  return defaultProfile
}