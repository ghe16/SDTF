export const mockAlgorithms = [
  {
    id: 'paxos',
    name: 'Paxos',
    description: 'Classic consensus algorithm for fault-tolerant distributed systems',
    status: 'active',
  },
  {
    id: 'raft',
    name: 'Raft',
    description: 'Consensus algorithm with leader-based approach and log replication',
    status: 'active',
  },
  {
    id: 'etcd',
    name: 'etcd',
    description: 'Distributed key-value store implementing Raft consensus',
    status: 'active',
  },
  {
    id: 'ot',
    name: 'Operational Transform',
    description: 'Conflict resolution for collaborative text editing',
    status: 'leader',
  },
  {
    id: 'crdt',
    name: 'CRDT',
    description: 'Conflict-free replicated data types for eventual consistency',
    status: 'active',
  },
  {
    id: 'wal',
    name: 'WAL',
    description: 'Write-Ahead Log for durability and crash recovery',
    status: 'active',
  },
  {
    id: '2pc',
    name: '2PC',
    description: 'Two-Phase Commit for distributed transaction atomicity',
    status: 'inactive',
  },
  {
    id: '3pc',
    name: '3PC',
    description: 'Three-Phase Commit with improved failure handling',
    status: 'inactive',
  },
  {
    id: 'gossip',
    name: 'Gossip Protocol',
    description: 'Epidemic broadcast for scalable peer-to-peer state',
    status: 'active',
  },
  {
    id: 'primary-backup',
    name: 'Primary-Backup',
    description: 'Simple replication model with primary node coordination',
    status: 'active',
  },
  {
    id: 'leader-election',
    name: 'Leader Election',
    description: 'Dynamic leader selection for cluster coordination',
    status: 'leader',
  },
]

export const mockNodes = [
  { id: 'node-001', ip: '10.0.1.101', role: 'leader', status: 'active', cpu: 45, memory: 62 },
  { id: 'node-002', ip: '10.0.1.102', role: 'follower', status: 'active', cpu: 32, memory: 48 },
  { id: 'node-003', ip: '10.0.1.103', role: 'follower', status: 'active', cpu: 28, memory: 41 },
  { id: 'node-004', ip: '10.0.1.104', role: 'follower', status: 'active', cpu: 51, memory: 73 },
  { id: 'node-005', ip: '10.0.1.105', role: 'follower', status: 'warning', cpu: 89, memory: 91 },
]

export const mockMetrics = {
  totalNodes: 12,
  activeNodes: 11,
  clusterHealth: 98.5,
  totalThroughput: '245.2K ops/s',
  avgLatency: '8.2ms',
}

export const mockLogs = [
  { id: 1, time: '14:32:01.421', level: 'INFO', message: 'Node node-002 heartbeat received' },
  { id: 2, time: '14:32:01.418', level: 'INFO', message: 'Leader election started' },
  { id: 3, time: '14:32:01.415', level: 'DEBUG', message: 'State machine applying entry #4821' },
  { id: 4, time: '14:32:01.412', level: 'WARN', message: 'High memory usage on node-005' },
  { id: 5, time: '14:32:01.409', level: 'INFO', message: 'Raft commit index updated to 4821' },
  { id: 6, time: '14:32:01.406', level: 'DEBUG', message: 'AppendEntries sent to 4 followers' },
  { id: 7, time: '14:32:01.403', level: 'INFO', message: 'Snapshot saved at index 4800' },
  { id: 8, time: '14:32:01.400', level: 'INFO', message: 'node-003 joined cluster' },
]

export const mockTopology = {
  nodes: [
    { id: 'node-001', x: 50, y: 50, type: 'leader' },
    { id: 'node-002', x: 30, y: 80, type: 'follower' },
    { id: 'node-003', x: 70, y: 80, type: 'follower' },
    { id: 'node-004', x: 20, y: 30, type: 'follower' },
    { id: 'node-005', x: 80, y: 30, type: 'follower' },
  ],
  links: [
    { source: 'node-001', target: 'node-002' },
    { source: 'node-001', target: 'node-003' },
    { source: 'node-001', target: 'node-004' },
    { source: 'node-001', target: 'node-005' },
  ],
}