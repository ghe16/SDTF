"""
Default mock engine - provides current mock behavior.
Used when no specific algorithm engine is implemented.
"""

import random
from app.core.engine import (
    AlgorithmEngine,
    register,
    EngineState,
    EngineResult,
    EngineValidation,
)


@register("etcd")
@register("leader-election")
@register("ot")
@register("crdt")
@register("2pc")
@register("3pc")
@register("gossip")
@register("primary-backup")
class MockEngine(AlgorithmEngine):
    """Mock engine that replicates current behavior."""
    
    MAX_TIME = 10.0
    
    def _create_initial_state(self, node_count: int, config: dict, scenario: dict = None) -> EngineState:
        # Generate star topology
        nodes = [{"id": f"n{i}", "label": f"Node {i}"} for i in range(node_count)]
        edges = [{"from": "n0", "to": f"n{i}"} for i in range(1, node_count)]
        
        node_states = {f"n{i}": "follower" for i in range(node_count)}
        node_states["n0"] = "leader"
        
        return EngineState(
            current_time=0.0,
            node_states=node_states,
            nodes=nodes,
            edges=edges,
            events=[],
        )
    
    def _create_initial_logs(self) -> list:
        return [
            {"time": "00:00:01.000", "level": "INFO", "message": "Execution started"},
            {"time": "00:00:01.500", "level": "INFO", "message": "Nodes initialized"},
        ]
    
    def step(self) -> None:
        """Advance time and generate mock events."""
        self._step_count += 1
        self._state.current_time = min(self._step_count * 0.5, self.MAX_TIME)
        
        # Generate events based on time
        if 1.0 <= self._state.current_time < 2.0:
            self._state.events = [{"time": 1, "type": "election", "label": "Elect leader"}]
            self._state.node_states = {f"n{i}": "follower" for i in range(len(self._state.nodes))}
            self._state.node_states["n0"] = "leader"
            self._add_log("00:00:02.000", "INFO", "Leader election initiated")
            self._add_log("00:00:02.500", "INFO", "Leader elected: node-0")
        
        elif 2.0 <= self._state.current_time < 4.0:
            self._state.events = [
                {"time": 2, "type": "proposal", "label": "Propose"},
                {"time": 3, "type": "vote", "label": "Vote"},
            ]
            self._state.node_states = {f"n{i}": "candidate" for i in range(len(self._state.nodes))}
            self._add_log("00:00:03.000", "DEBUG", "Proposing value v1")
            self._add_log("00:00:03.200", "INFO", "Vote received from node-1")
            self._add_log("00:00:03.400", "INFO", "Vote received from node-2")
        
        elif 4.0 <= self._state.current_time < 6.0:
            self._state.events = [{"time": 4, "type": "commit", "label": "Commit"}]
            self._state.node_states = {f"n{i}": "follower" for i in range(len(self._state.nodes))}
            self._state.node_states["n0"] = "leader"
            self._add_log("00:00:03.600", "INFO", "Entry committed")
            self._add_log("00:00:04.000", "DEBUG", "Replicating to followers")
            self._add_log("00:00:04.500", "INFO", "All nodes synchronized")
    
    def get_result(self) -> EngineResult:
        return EngineResult(
            rounds=42,
            decisions=38,
            avg_latency=12.5,
            success_rate=95.2,
        )
    
    def get_validation(self, result: EngineResult) -> EngineValidation:
        success = result.success_rate >= 90 and result.avg_latency < 50
        
        invariants = [
            {"name": "Safety", "description": "No two nodes decide different values", "holds": result.success_rate >= 95},
            {"name": "Liveness", "description": "Eventually every correct node decides", "holds": result.success_rate >= 90},
            {"name": "Termination", "description": "All nodes terminate", "holds": result.success_rate >= 95},
            {"name": "Consistency", "description": "All nodes see same state", "holds": result.success_rate >= 90},
            {"name": "LeaderValidity", "description": "If leader decides, it proposed it", "holds": result.success_rate >= 85},
        ]
        
        passed = sum(1 for i in invariants if i["holds"])
        explanation = (
            f"All {passed}/5 invariants hold. The algorithm correctly achieved consensus with {result.success_rate}% success rate."
            if success
            else f"{5 - passed} invariant(s) violated. The algorithm failed to maintain consistency under the given conditions."
        )
        
        return EngineValidation(success=success, explanation=explanation, invariants=invariants)
    
    def is_finished(self) -> bool:
        return self._state.current_time >= self.MAX_TIME