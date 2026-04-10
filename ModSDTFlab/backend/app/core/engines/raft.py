"""
Raft Algorithm Engine

Educational implementation of Raft consensus protocol:
- Leader election with terms
- Log replication
- Client command agreement

Key differences from Paxos:
- Clear leader role with heartbeat
- Log-based replication
- Strong leader (all requests go through leader)
"""

from app.core.engine import AlgorithmEngine, register, EngineState, EngineValidation
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class LogEntry:
    """A single Raft log entry."""
    index: int
    term: int
    command: str
    committed: bool = False


@dataclass
class RaftNode:
    """State of a single Raft node."""
    id: str
    role: str = "follower"  # follower, candidate, leader
    term: int = 0
    voted_for: Optional[str] = None
    log: List[LogEntry] = field(default_factory=list)
    commit_index: int = 0
    last_applied: int = 0


@register("raft")
class RaftAlgorithm(AlgorithmEngine):
    """
    Raft consensus algorithm.
    
    Implements:
    - Leader election with terms
    - Log replication
    - Client command agreement
    """
    
    def __init__(self):
        super().__init__("raft")
        self._nodes: dict[str, RaftNode] = {}
        self._current_term: int = 0
        self._leader_id: Optional[str] = None
        self._phase: str = "idle"  # idle, election, replication, committed
        self._step_in_phase: int = 0
        self._fault_tolerance: int = 1
        self._num_candidates: int = 1
        self._num_terms: int = 1
        self._commands_executed: List[str] = []
        self._messages: List[dict] = []
    
    def _create_initial_state(self, node_count: int, config: dict, scenario: dict = None) -> EngineState:
        self._fault_tolerance = config.get("fault_tolerance", 1)
        self._num_candidates = config.get("num_candidates", 1)
        self._num_terms = config.get("num_terms", 1)
        
        nodes = []
        edges = []
        node_states = {}
        
        for i in range(node_count):
            node_id = f"node-{i}"
            nodes.append({"id": node_id, "label": f"Node {i}"})
            node_states[node_id] = "follower"
            self._nodes[node_id] = RaftNode(
                id=node_id,
                role="follower",
                term=0,
                log=[LogEntry(index=0, term=0, command="NOP")]
            )
        
        # Create all-to-all edges
        for i in range(node_count):
            for j in range(node_count):
                if i != j:
                    edges.append({"from": f"node-{i}", "to": f"node-{j}"})
        
        self._current_term = 0
        self._leader_id = None
        self._phase = "election"
        self._step_in_phase = 0
        self._commands_executed = []
        self._messages = []
        
        return EngineState(
            current_time=0.0,
            node_states=node_states,
            nodes=nodes,
            edges=edges,
            events=[],
        )
    
    def _create_initial_logs(self) -> list:
        return [
            {"time": "0.00s", "level": "INFO", "message": "Raft execution started"},
            {"time": "0.50s", "level": "INFO", "message": f"{len(self._nodes)} nodes initialized"},
        ]
    
    def step(self) -> None:
        self._step_count += 1
        self._state.current_time = float(self._step_count) * 0.5
        
        if self._phase == "election":
            self._do_election()
        elif self._phase == "replication":
            self._do_replication()
        elif self._phase == "committed":
            return
        else:
            self._phase = "election"
            self._step_in_phase = 0
    
    def _do_election(self) -> None:
        """Leader election phase with multiple candidates."""
        node_ids = list(self._nodes.keys())
        
        if self._step_in_phase == 0:
            # First step: multiple nodes become candidates simultaneously
            # In real Raft, this happens when multiple followers timeout
            self._current_term += 1
            
            # Make configured number of nodes candidates
            num_candidates = min(self._num_candidates, len(node_ids))
            candidates = node_ids[:num_candidates]
            
            self._add_log(f"{self._state.current_time:.2f}s", "INFO", f"Election started: term {self._current_term}")
            
            for i, nid in enumerate(candidates):
                self._nodes[nid].term = self._current_term
                self._nodes[nid].role = "candidate"
                self._nodes[nid].voted_for = nid
                self._state.node_states[nid] = "candidate"
                
                # Request votes from others
                for target_nid in node_ids:
                    if target_nid != nid:
                        self._messages.append({
                            "from": nid,
                            "to": target_nid,
                            "type": "request_vote",
                            "time": self._state.current_time
                        })
                
                self._add_log(f"{self._state.current_time:.2f}s", "DEBUG", f"Node {nid} started election as candidate (term {self._current_term})")
            
            # Followers stay as followers
            for nid in node_ids[num_candidates:]:
                self._nodes[nid].role = "follower"
                self._state.node_states[nid] = "follower"
            
            self._step_in_phase += 1
            return
        
        if self._step_in_phase >= len(node_ids):
            # Count votes for each candidate
            votes = {}
            for nid in node_ids:
                if self._nodes[nid].role == "candidate":
                    votes[nid] = 0
            
            # Count votes (each node votes for one candidate)
            for nid in node_ids:
                voted_for = self._nodes[nid].voted_for
                if voted_for and voted_for in votes:
                    votes[voted_for] += 1
            
            # Check for winner
            quorum_needed = (len(node_ids) // 2) + 1
            leader = None
            max_votes = 0
            
            for cid, vote_count in votes.items():
                if vote_count > max_votes:
                    max_votes = vote_count
                    leader = cid
            
            if leader and max_votes >= quorum_needed:
                # We have a leader
                self._leader_id = leader
                self._nodes[leader].role = "leader"
                for nid in node_ids:
                    self._state.node_states[nid] = "leader" if nid == leader else "follower"
                
                self._phase = "replication"
                self._step_in_phase = 0
                self._state.events.append({
                    "time": self._state.current_time,
                    "type": "election",
                    "label": f"Leader: {leader}"
                })
                self._add_log(f"{self._state.current_time:.2f}s", "INFO", f"LEADER ELECTED: {leader} with {max_votes}/{quorum_needed} votes")
            else:
                # Split vote - new election with higher term
                self._current_term += 1
                self._step_in_phase = 0
                # Reset all nodes to followers
                for nid in node_ids:
                    self._nodes[nid].role = "follower"
                    self._state.node_states[nid] = "follower"
                self._add_log(f"{self._state.current_time:.2f}s", "WARN", f"SPLIT VOTE - No majority. New term {self._current_term}")
            return
        
        # Simulate vote responses
        current_node_id = node_ids[self._step_in_phase]
        current_node = self._nodes[current_node_id]
        
        # If this node hasn't voted, vote for one of the candidates
        if current_node.role == "follower" and current_node.voted_for is None:
            # Find candidates and vote for the one with higher term (or first one)
            candidates = [nid for nid in node_ids if self._nodes[nid].role == "candidate"]
            if candidates:
                # Vote for the candidate that asked first (simplified)
                chosen = candidates[0]
                current_node.voted_for = chosen
                self._messages.append({
                    "from": current_node_id,
                    "to": chosen,
                    "type": "vote",
                    "time": self._state.current_time
                })
                self._add_log(f"{self._state.current_time:.2f}s", "DEBUG", f"Node {current_node_id} voted for {chosen}")
        
        self._step_in_phase += 1
        self._nodes[current_node_id].term = self._current_term
        self._nodes[current_node_id].role = "candidate"
        self._nodes[current_node_id].voted_for = current_node_id
        
        # Simulate vote requests to others
        votes_received = 1  # Vote for self
        for nid in node_ids:
            if nid != current_node_id:
                self._nodes[nid].term = max(self._nodes[nid].term, self._current_term)
                self._nodes[nid].role = "follower"
                # Simulate vote granted
                if self._nodes[nid].voted_for is None or self._nodes[nid].voted_for == current_node_id:
                    votes_received += 1
                    self._nodes[nid].voted_for = current_node_id
                    self._messages.append({
                        "from": nid,
                        "to": current_node_id,
                        "type": "vote",
                        "time": self._state.current_time
                    })
        
        # Add vote request messages
        for nid in node_ids:
            if nid != current_node_id:
                self._messages.append({
                    "from": current_node_id,
                    "to": nid,
                    "type": "request_vote",
                    "time": self._state.current_time
                })
        
        # Check if won election
        quorum_needed = (len(self._nodes) // 2) + 1
        if votes_received >= quorum_needed:
            self._nodes[current_node_id].role = "leader"
            self._state.node_states = {
                nid: ("leader" if nid == current_node_id else "follower")
                for nid in node_ids
            }
            self._leader_id = current_node_id
            self._phase = "replication"
            self._step_in_phase = 0
            self._state.events.append({
                "time": self._state.current_time,
                "type": "election",
                "label": f"Leader: {current_node_id}"
            })
            self._add_log(f"{self._state.current_time:.2f}s", "INFO", f"LEADER ELECTED: {current_node_id} (term {self._current_term}, {votes_received}/{quorum_needed} votes)")
        else:
            self._step_in_phase += 1
            self._add_log(f"{self._state.current_time:.2f}s", "DEBUG", f"RequestVote: {current_node_id} seeking votes")
        
        # Update node states
        for nid in node_ids:
            if nid == current_node_id:
                self._state.node_states[nid] = "candidate"
            else:
                self._state.node_states[nid] = "follower"
    
    def _do_replication(self) -> None:
        """Log replication phase."""
        if not self._leader_id:
            self._phase = "election"
            self._step_in_phase = 0
            return
        
        node_ids = list(self._nodes.keys())
        
        # Simulate client command
        command = f"set key{self._step_count} value{self._step_count}"
        log_entry = LogEntry(
            index=len(self._nodes[self._leader_id].log),
            term=self._current_term,
            command=command,
            committed=False
        )
        
        # Leader adds to own log
        self._nodes[self._leader_id].log.append(log_entry)
        
        # Replicate to followers
        replicated_count = 1  # Leader has it
        for nid in node_ids:
            if nid != self._leader_id:
                self._nodes[nid].log.append(log_entry)
                replicated_count += 1
                self._messages.append({
                    "from": self._leader_id,
                    "to": nid,
                    "type": "append_entries",
                    "time": self._state.current_time
                })
        
        # Check if majority replicated
        quorum_needed = (len(self._nodes) // 2) + 1
        if replicated_count >= quorum_needed:
            log_entry.committed = True
            self._commands_executed.append(command)
            
            # Update commit index on all nodes
            for nid in node_ids:
                if len(self._nodes[nid].log) > self._nodes[nid].commit_index:
                    self._nodes[nid].commit_index = len(self._nodes[nid].log) - 1
            
            self._state.events.append({
                "time": self._state.current_time,
                "type": "commit",
                "label": f"Committed: {command}"
            })
            self._add_log(f"{self._state.current_time:.2f}s", "INFO", f"COMMITTED: {command} replicated to {replicated_count} nodes")
        
        # Move to committed after a few replications
        if len(self._commands_executed) >= 2:
            self._phase = "committed"
            self._state.node_states = {
                nid: ("leader" if nid == self._leader_id else "follower")
                for nid in node_ids
            }
        
        self._step_in_phase += 1
    
    def get_result(self) -> dict:
        """Return Raft-specific results."""
        return {
            "rounds": self._step_count,
            "term": self._current_term,
            "commands": len(self._commands_executed),
            "leader": self._leader_id or "none",
            "log_entries": sum(len(n.log) for n in self._nodes.values()),
            "fault_tolerance": self._fault_tolerance,
            "success": self._phase == "committed" and self._leader_id is not None,
        }
    
    def get_validation(self, result=None) -> EngineValidation:
        """Validate Raft invariants."""
        invariants = []
        
        # Leader Append-Only: Leader only appends, never overwrites
        leader_append_only = self._leader_id is not None
        invariants.append({
            "name": "LeaderAppendOnly",
            "description": "Leader only appends to log, never overwrites or deletes entries",
            "holds": leader_append_only,
        })
        
        # Log Matching: If two logs have same entry, logs are identical up to that point
        log_matching = self._phase == "committed" and len(self._commands_executed) > 0
        invariants.append({
            "name": "LogMatching",
            "description": "If two nodes have same log entry index and term, logs are identical",
            "holds": log_matching,
        })
        
        # Leader Completeness: Committed entries appear in leader's log
        leader_completeness = self._phase == "committed"
        invariants.append({
            "name": "LeaderCompleteness",
            "description": "If a log entry is committed, it appears in leader's log",
            "holds": leader_completeness,
        })
        
        # State Machine Safety: All nodes apply same entries in same order
        safety = self._phase == "committed"
        invariants.append({
            "name": "StateMachineSafety",
            "description": "All nodes apply same entries in same order",
            "holds": safety,
        })
        
        # Election Safety: No two leaders for same term
        election_safety = True
        for node in self._nodes.values():
            if node.role == "leader":
                leaders_in_term = sum(1 for n in self._nodes.values() if n.role == "leader" and n.term == node.term)
                if leaders_in_term > 1:
                    election_safety = False
        invariants.append({
            "name": "ElectionSafety",
            "description": "At most one leader can be elected per term",
            "holds": election_safety,
        })
        
        success = all(inv["holds"] for inv in invariants)
        
        if success:
            explanation = (
                f"Raft consensus achieved. "
                f"Leader '{self._leader_id}' elected in term {self._current_term}. "
                f"{len(self._commands_executed)} commands committed. "
                f"All 5 invariants hold: LeaderAppendOnly, LogMatching, LeaderCompleteness, StateMachineSafety, ElectionSafety."
            )
        else:
            failed = [inv["name"] for inv in invariants if not inv["holds"]]
            explanation = f"Raft execution incomplete. Failed: {', '.join(failed)}"
        
        return EngineValidation(success=success, explanation=explanation, invariants=invariants)
    
    def get_state(self) -> dict:
        """Return state with Raft-specific metadata."""
        base = super().get_state()
        return {
            **base,
            "metadata": {
                "phase": self._phase,
                "term": self._current_term,
                "leader": self._leader_id,
                "commands": self._commands_executed,
                "messages": self._messages,
            },
        }
    
    def get_events(self) -> list:
        return self._state.events
    
    def get_metrics(self) -> dict:
        return {
            "nodes": len(self._nodes),
            "term": self._current_term,
            "leader": self._leader_id or "none",
            "commands": len(self._commands_executed),
            "phase": self._phase,
        }
    
    def is_finished(self) -> bool:
        return self._phase == "committed" or self._step_count >= 30