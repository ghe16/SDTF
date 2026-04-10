"""
WAL (Write-Ahead Logging) - Student Implementation

This is the student version of the WAL algorithm.
Complete the TODO sections to implement the WAL logic.

Reference solution is in wal.py - do not modify that file.
Students should only modify THIS file.
"""

from app.core.engine import AlgorithmEngine, register, EngineState, EngineValidation
from dataclasses import dataclass
from typing import Optional


@dataclass
class LogEntry:
    """A single WAL log entry."""
    index: int
    operation: str
    key: str
    value: str
    committed: bool = False


@register("wal-student")
class WALStudentAlgorithm(AlgorithmEngine):
    """
    Write-Ahead Logging - Student Implementation
    
    Implement the core WAL steps:
    1. Receive operation from client
    2. Append to WAL log
    3. Flush/commit log entry
    4. Apply to storage
    5. Handle crash and recovery
    """
    
    def __init__(self):
        super().__init__("wal-student")
        # TODO: Initialize your state fields
        # - scenario
        # - operations list
        # - log list
        # - data_store dict
        # - current operation index
        # - step within operation
        pass
    
    def _create_initial_state(self, node_count: int, config: dict, scenario: dict = None) -> EngineState:
        """
        Initialize the WAL state.
        Graph structure: client -> WAL -> storage
        """
        # TODO: Parse scenario and config
        # Store the scenario name and operations
        
        # TODO: Initialize empty log and data store
        
        return EngineState(
            current_time=0.0,
            node_states={
                "client": "idle",
                "wal": "ready",
                "storage": "ready",
            },
            nodes=[
                {"id": "client", "label": "Client"},
                {"id": "wal", "label": "WAL"},
                {"id": "storage", "label": "Storage"},
            ],
            edges=[
                {"from": "client", "to": "wal"},
                {"from": "wal", "to": "storage"},
            ],
            events=[],
            scenario="normal_write",
        )
    
    def _create_initial_logs(self) -> list:
        """Create initial log entries."""
        return [
            {"time": "0.00s", "level": "INFO", "message": "WAL Student started"},
        ]
    
    def step(self) -> None:
        """
        Execute one step of the WAL algorithm.
        
        Each operation takes 4 steps:
        - Step 0: Receive request from client
        - Step 1: Append to WAL log
        - Step 2: Flush/commit log entry
        - Step 3: Apply to storage
        """
        self._step_count += 1
        self._state.current_time = float(self._step_count) * 0.5
        
        # TODO: Implement the step logic
        
        # Check if all operations are done
        # If crashed, handle recovery
        # Otherwise process current operation based on _step_in_op
        
        # Example structure:
        # if crashed and not recovered:
        #     self._do_recovery()
        # elif _step_in_op == 0:
        #     # Receive request
        # elif _step_in_op == 1:
        #     # Append to log
        # elif _step_in_op == 2:
        #     # Flush log
        # elif _step_in_op == 3:
        #     # Apply to storage
        
        pass
    
    def _trigger_crash(self) -> None:
        """Trigger a crash simulation."""
        # TODO: Set crashed state, update node states
        pass
    
    def _do_recovery(self) -> None:
        """Recover from crash by replaying committed log entries."""
        # TODO: 
        # 1. Set recovered state
        # 2. Update node states to recovering
        # 3. For each log entry:
        #    - if committed: replay (apply to data store)
        #    - if not committed: skip (don't apply)
        # 4. Log recovery progress
        pass
    
    def get_result(self) -> dict:
        """Return execution results."""
        # TODO: Return a dict with:
        # - steps: total step count
        # - operations: number of operations
        # - log_entries: number of log entries
        # - stored_keys: number of keys in data store
        # - crashed: whether crash occurred
        # - recovered: whether recovered from crash
        # - success: overall success flag
        return {"steps": 0, "operations": 0, "log_entries": 0, "stored_keys": 0, "crashed": False, "recovered": False, "success": True}
    
    def get_validation(self, result=None) -> EngineValidation:
        """Validate WAL invariants."""
        # TODO: Check invariants like:
        # - WriteAheadProperty: no uncommitted data in storage
        # - RecoveryCorrectness: all committed entries recovered
        # - DataConsistency: data store matches committed entries
        
        invariants = [
            {"name": "WriteAheadProperty", "description": "Data not in storage before log flush", "holds": True},
        ]
        return EngineValidation(
            success=True,
            explanation="Validation complete",
            invariants=invariants,
        )
    
    def is_finished(self) -> bool:
        """Check if execution is finished."""
        # TODO: Return True when all operations processed and any recovery done
        return False


# STUDENT TASKS:
# 1. Implement __init__ - initialize state fields
# 2. Implement _create_initial_state - setup graph and state
# 3. Implement step - process one step of WAL
# 4. Implement _trigger_crash - handle crash
# 5. Implement _do_recovery - replay committed entries
# 6. Implement get_result - return metrics
# 7. Implement get_validation - check invariants
# 8. Implement is_finished - check completion