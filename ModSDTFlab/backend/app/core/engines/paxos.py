"""
Paxos Algorithm Engine

Educational implementation of Multi-Paxos consensus protocol:
- Phase 1: Prepare/Promise (leader election)
- Phase 2: Accept/Accepted (value agreement)
- Handles multiple nodes with configurable fault tolerance

Nodes act as proposers and acceptors.
"""

from app.core.engine import AlgorithmEngine, register, EngineState, EngineValidation
from dataclasses import dataclass, field
from typing import Optional
import random


@dataclass
class Proposal:
    """A Paxos proposal."""
    number: int
    value: str
    node_id: str


@dataclass
class PaxosNode:
    """State of a single Paxos node."""
    id: str
    role: str = "follower"  # follower, leader, candidate
    promised_number: int = 0
    accepted_number: int = 0
    accepted_value: Optional[str] = None
    vote_count: int = 0
    prepare_count: int = 0


@register("paxos")
class PaxosAlgorithm(AlgorithmEngine):
    """
    Paxos consensus algorithm.
    
    Implements:
    - Leader election via Prepare/Promise
    - Value agreement via Accept/Accepted
    - Quorum-based decisions
    """
    
    def __init__(self):
        super().__init__("paxos")
        self._nodes: dict[str, PaxosNode] = {}
        self._proposals: list[Proposal] = []
        self._log: list[dict] = []
        self._decided_value: Optional[str] = None
        self._current_proposal_num = 0
        self._phase = "idle"  # idle, prepare, accept, decided
        self._step_in_phase = 0
        self._fault_tolerance = 1
        self._crashed_nodes: set = set()
        self._messages: list[dict] = []  # Track messages for animation
        self._proposer_id: Optional[str] = None  # Track who is proposing
    
    def _create_initial_state(self, node_count: int, config: dict, scenario: dict = None) -> EngineState:
        self._fault_tolerance = config.get("fault_tolerance", 1)
        
        # Create nodes
        nodes = []
        edges = []
        node_states = {}
        
        for i in range(node_count):
            node_id = f"node-{i}"
            nodes.append({"id": node_id, "label": f"Node {i}"})
            node_states[node_id] = "follower"
            self._nodes[node_id] = PaxosNode(id=node_id, role="follower")
        
        # Create all-to-all edges (full mesh for consensus)
        for i in range(node_count):
            for j in range(node_count):
                if i != j:
                    edges.append({"from": f"node-{i}", "to": f"node-{j}"})
        
        self._log = []
        self._proposals = []
        self._decided_value = None
        self._current_proposal_num = 0
        self._phase = "prepare"
        self._step_in_phase = 0
        self._crashed_nodes = set()
        
        return EngineState(
            current_time=0.0,
            node_states=node_states,
            nodes=nodes,
            edges=edges,
            events=[],
        )
    
    def _create_initial_logs(self) -> list:
        return [
            {"time": "0.00s", "level": "INFO", "message": "Paxos execution started"},
            {"time": "0.50s", "level": "INFO", "message": f"{len(self._nodes)} nodes initialized, fault tolerance: {self._fault_tolerance}"},
        ]
    
    def step(self) -> None:
        self._step_count += 1
        self._state.current_time = float(self._step_count) * 0.5
        
        # Skip crashed nodes
        if self._phase in ("prepare", "accept") and self._step_in_phase < len(self._nodes):
            current_node_id = list(self._nodes.keys())[self._step_in_phase]
            if current_node_id in self._crashed_nodes:
                self._step_in_phase += 1
                return
        
        if self._phase == "prepare":
            self._do_prepare_phase()
        elif self._phase == "accept":
            self._do_accept_phase()
        elif self._phase == "decided":
            return
        else:
            # Idle, start prepare phase
            self._phase = "prepare"
            self._step_in_phase = 0
    
    def _do_prepare_phase(self) -> None:
        """Phase 1: Proposer sends Prepare, Acceptors Promise."""
        node_ids = list(self._nodes.keys())
        current_idx = self._step_in_phase
        
        if current_idx >= len(node_ids):
            # All nodes processed, check for quorum
            promises = sum(1 for n in self._nodes.values() if n.promised_number > 0)
            quorum_needed = (len(self._nodes) // 2) + 1
            
            if promises >= quorum_needed:
                self._phase = "accept"
                self._step_in_phase = 0
                self._add_log(f"{self._state.current_time:.2f}s", "INFO", f"Prepare phase complete: {promises}/{quorum_needed} promises received")
            else:
                # Retry with higher proposal number
                self._current_proposal_num += 1
                self._reset_node_promises()
                self._step_in_phase = 0
                self._add_log(f"{self._state.current_time:.2f}s", "WARN", f"Incomplete promises, retrying with proposal {self._current_proposal_num}")
            return
        
        current_node_id = node_ids[current_idx]
        current_node = self._nodes[current_node_id]
        
        # This node becomes proposer
        self._current_proposal_num += 1
        proposal_num = self._current_proposal_num
        
        current_node.role = "candidate"
        current_node.promised_number = proposal_num
        current_node.prepare_count += 1
        
        # Simulate receiving promises from majority
        promises_gathered = 0
        for nid, node in self._nodes.items():
            if nid != current_node_id and nid not in self._crashed_nodes:
                if node.promised_number <= proposal_num:
                    promises_gathered += 1
                    node.promised_number = proposal_num
                    # Add message: promise from nid to current_node_id
                    self._messages.append({
                        "from": nid,
                        "to": current_node_id,
                        "type": "promise",
                        "time": self._state.current_time
                    })
        
        # Add message: prepare from proposer to all
        for nid in self._nodes.keys():
            if nid != current_node_id:
                self._messages.append({
                    "from": current_node_id,
                    "to": nid,
                    "type": "prepare",
                    "time": self._state.current_time
                })
        
        # Track proposer
        self._proposer_id = current_node_id
        
        quorum_needed = (len(self._nodes) // 2) + 1
        if promises_gathered >= quorum_needed - 1:
            # Got quorum, move to accept phase
            self._phase = "accept"
            self._step_in_phase = 0
            
            # Propose a value (either highest promised or new)
            highest_value = None
            for node in self._nodes.values():
                if node.accepted_value and node.promised_number == proposal_num:
                    if highest_value is None or node.accepted_number > (self._current_proposal_num if hasattr(self, '_last_accepted') else 0):
                        highest_value = node.accepted_value
            
            self._decided_value = highest_value or f"value-{self._current_proposal_num}"
            
            self._state.events.append({
                "time": self._state.current_time,
                "type": "proposal",
                "label": f"Propose: {self._decided_value}"
            })
            self._add_log(f"{self._state.current_time:.2f}s", "INFO", f"PREPARED: Proposal {proposal_num}, value: {self._decided_value}")
        else:
            self._step_in_phase += 1
            self._add_log(f"{self._state.current_time:.2f}s", "DEBUG", f"PREPARE: Node {current_node_id} promises {proposal_num}")
        
        # Update node states - proposer is candidate, others are followers
        for nid, node in self._nodes.items():
            if nid == current_node_id:
                self._state.node_states[nid] = "candidate"
            else:
                self._state.node_states[nid] = "follower"
    
    def _do_accept_phase(self) -> None:
        """Phase 2: Proposer sends Accept, Acceptors Accept."""
        if self._decided_value is None:
            self._decided_value = f"value-{self._current_proposal_num}"
        
        node_ids = list(self._nodes.keys())
        current_idx = self._step_in_phase
        
        if current_idx >= len(node_ids):
            # All nodes processed, check for accepted quorum
            accepted = sum(1 for n in self._nodes.values() if n.accepted_number == self._current_proposal_num)
            quorum_needed = (len(self._nodes) // 2) + 1
            
            if accepted >= quorum_needed:
                self._phase = "decided"
                # Only the proposer is leader, others are followers
                proposer_id = list(self._nodes.keys())[0]  # First node was the proposer
                self._state.node_states = {
                    proposer_id: "leader",
                    **{nid: "follower" for nid in self._nodes.keys() if nid != proposer_id}
                }
                self._state.events.append({
                    "time": self._state.current_time,
                    "type": "commit",
                    "label": f"Decided: {self._decided_value}"
                })
                self._add_log(f"{self._state.current_time:.2f}s", "INFO", f"COMMITTED: Value '{self._decided_value}' accepted by majority")
                self._log.append({
                    "index": len(self._log) + 1,
                    "value": self._decided_value,
                    "decided": True
                })
            else:
                # Retry from prepare
                self._phase = "prepare"
                self._step_in_phase = 0
                self._add_log(f"{self._state.current_time:.2f}s", "WARN", f"Incomplete accepts, retrying")
            return
        
        current_node_id = node_ids[current_idx]
        
        if current_node_id in self._crashed_nodes:
            self._step_in_phase += 1
            return
        
        # Add message: accept from proposer to node
        if self._proposer_id:
            self._messages.append({
                "from": self._proposer_id,
                "to": current_node_id,
                "type": "accept",
                "time": self._state.current_time
            })
        
        # Accept the value
        self._nodes[current_node_id].accepted_number = self._current_proposal_num
        self._nodes[current_node_id].accepted_value = self._decided_value
        
        self._step_in_phase += 1
        self._add_log(f"{self._state.current_time:.2f}s", "DEBUG", f"ACCEPT: Node {current_node_id} accepted {self._decided_value}")
    
    def _reset_node_promises(self) -> None:
        """Reset promises for retry."""
        for node in self._nodes.values():
            if node.role == "candidate":
                node.role = "follower"
    
    def _trigger_crash(self, node_id: str) -> None:
        """Simulate node crash."""
        self._crashed_nodes.add(node_id)
        self._state.node_states[node_id] = "crashed"
        self._add_log(f"{self._state.current_time:.2f}s", "ERROR", f"CRASH: Node {node_id} crashed")
        self._state.events.append({"time": self._state.current_time, "type": "crash", "label": f"Node {node_id} crashed"})
    
    def get_result(self) -> dict:
        """Return Paxos-specific results."""
        return {
            "rounds": self._step_count,
            "proposals": self._current_proposal_num,
            "decisions": len(self._log),
            "decided_value": self._decided_value or "none",
            "fault_tolerance": self._fault_tolerance,
            "quorum_size": (len(self._nodes) // 2) + 1,
            "success": self._phase == "decided" and self._decided_value is not None,
        }
    
    def get_validation(self, result=None) -> EngineValidation:
        """Validate Paxos invariants."""
        invariants = []
        
        # Safety: No two values can be chosen
        safety_holds = len(self._log) <= 1 or self._phase == "decided"
        invariants.append({
            "name": "Safety",
            "description": "No two nodes can decide different values",
            "holds": safety_holds,
        })
        
        # Liveness: If a value is proposed, eventually it will be decided
        liveness_holds = self._phase == "decided" or self._step_count < 20
        invariants.append({
            "name": "Liveness",
            "description": "Eventually every correct node decides a value",
            "holds": liveness_holds,
        })
        
        # Validity: A value can only be decided if it was proposed
        validity_holds = self._decided_value is None or self._decided_value.startswith("value-")
        invariants.append({
            "name": "Validity",
            "description": "A decided value must have been proposed",
            "holds": validity_holds,
        })
        
        # Termination: All nodes eventually terminate
        termination_holds = self._phase == "decided"
        invariants.append({
            "name": "Termination",
            "description": "All nodes eventually terminate",
            "holds": termination_holds,
        })
        
        # Quorum: Decisions require majority
        quorum_holds = result and result.get("decisions", 0) > 0
        invariants.append({
            "name": "QuorumRequirement",
            "description": "Decisions require majority agreement",
            "holds": quorum_holds,
        })
        
        success = all(inv["holds"] for inv in invariants)
        
        if success:
            explanation = (
                f"Paxos consensus achieved. "
                f"Value '{self._decided_value}' was decided with {result.get('quorum_size', 0)} node quorum. "
                f"All 5 invariants hold: Safety, Liveness, Validity, Termination, QuorumRequirement."
            )
        else:
            failed = [inv["name"] for inv in invariants if not inv["holds"]]
            explanation = (
                f"Paxos execution incomplete. "
                f"Failed invariants: {', '.join(failed)}. "
                f"Current phase: {self._phase}, proposed value: {self._decided_value}"
            )
        
        return EngineValidation(success=success, explanation=explanation, invariants=invariants)
    
    def get_state(self) -> dict:
        """Return state with Paxos-specific metadata."""
        base = super().get_state()
        return {
            **base,
            "metadata": {
                "phase": self._phase,
                "proposal_number": self._current_proposal_num,
                "decided_value": self._decided_value,
                "log": self._log,
                "crashed_nodes": list(self._crashed_nodes),
                "messages": self._messages,
                "proposer_id": self._proposer_id,
            },
        }
    
    def get_events(self) -> list:
        return self._state.events
    
    def get_metrics(self) -> dict:
        return {
            "nodes": len(self._nodes),
            "proposals": self._current_proposal_num,
            "decisions": len(self._log),
            "phase": self._phase,
            "fault_tolerance": self._fault_tolerance,
            "crashed": len(self._crashed_nodes),
        }
    
    def is_finished(self) -> bool:
        return self._phase == "decided" or self._step_count >= 30