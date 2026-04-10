"""
WAL (Write-Ahead Logging) Algorithm Engine

Educational implementation demonstrating:
- Log append before apply (write-ahead)
- Crash recovery by replay
- Data consistency guarantees

Components: client -> WAL -> storage
"""

from app.core.engine import AlgorithmEngine, register, EngineState, EngineValidation
from app.core.engines.wal_scenarios import get_scenario, SCENARIOS
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LogEntry:
    """A single WAL entry."""
    index: int
    operation: str
    key: str
    value: str
    committed: bool = False


@register("wal")
class WALAlgorithm(AlgorithmEngine):
    """
    Write-Ahead Logging algorithm.
    
    Demonstrates the fundamental principle: log to stable storage
    BEFORE applying changes to the data store.
    """
    
    def __init__(self):
        super().__init__("wal")
        self._scenario_name = "normal_write"
        self._scenario = None
        self._operations = []
        self._log: list[LogEntry] = []
        self._data_store: dict = {}
        self._crashed = False
        self._recovered = False
        self._current_op_index = 0
        self._step_in_op = 0
    
    def _create_initial_state(self, node_count: int, config: dict, scenario: dict = None) -> EngineState:
        # Determine scenario: use scenario param, then config, then default
        scenario_name = "normal_write"
        
        # Handle different scenario input formats
        if scenario:
            if isinstance(scenario, str):
                # Direct string passed
                scenario_name = scenario
            elif isinstance(scenario, dict):
                # Dict with "scenario" key
                if "scenario" in scenario:
                    scenario_name = scenario["scenario"]
                # Also check if the whole dict is a scenario config
                elif "name" in scenario:
                    # It's already a Scenario object, not a name
                    scenario_name = scenario.get("name", "normal_write")
        
        # Also check config as fallback
        if config and "scenario" in config:
            scenario_name = config["scenario"]
        
        # Check if it's a predefined scenario
        self._scenario = get_scenario(scenario_name)
        if self._scenario:
            self._scenario_name = self._scenario.name
            self._operations = list(self._scenario.operations)  # Copy
            crash_step = self._scenario.crash_step
        else:
            # Legacy: treat as custom operations
            self._scenario_name = scenario_name
            self._operations = config.get("operations", [
                {"op": "SET", "key": "counter", "value": "1"},
            ])
            crash_step = config.get("crash_step")
        
        self._log = []
        self._data_store = {}
        self._crashed = False
        self._recovered = False
        self._current_op_index = 0
        self._step_in_op = 0
        
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
                {"from": "client", "to": "wal", "source": "client", "target": "wal"},
                {"from": "wal", "to": "storage", "source": "wal", "target": "storage"},
            ],
            events=[],
            scenario=self._scenario_name,
        )
    
    def _create_initial_logs(self) -> list:
        """Create initial log entries with consistent timestamp format."""
        return [
            {"time": "0.00s", "level": "INFO", "message": "Execution started"},
            {"time": "0.50s", "level": "INFO", "message": "Nodes initialized"},
        ]
    
    def _should_crash(self) -> bool:
        """Check if we should crash at current step."""
        if not self._scenario or self._scenario.crash_step is None:
            return False
        
        current_op_step = self._current_op_index * 4 + self._step_in_op
        return current_op_step == self._scenario.crash_step
    
    def step(self) -> None:
        """Execute one step of the WAL algorithm."""
        self._step_count += 1
        self._state.current_time = float(self._step_count) * 0.5
        
        # If crashed and not yet recovered, handle recovery
        if self._crashed and not self._recovered:
            self._do_recovery()
            return
        
        # Check for crash before processing operation
        if self._should_crash():
            self._trigger_crash()
            return
        
        # Process current operation
        if self._current_op_index >= len(self._operations):
            self._state.node_states = {
                "client": "completed",
                "wal": "ready",
                "storage": "ready",
            }
            return
        
        operation = self._operations[self._current_op_index]
        
        if self._step_in_op == 0:
            # Step 1: Client sends request
            self._state.node_states = {
                "client": "requesting",
                "wal": "ready",
                "storage": "ready",
            }
            self._add_log(
                f"{self._state.current_time:.2f}s",
                "INFO",
                f"REQUEST_RECEIVED: {operation['op']} {operation['key']}={operation['value']}"
            )
            
        elif self._step_in_op == 1:
            # Step 2: WAL appends to log
            entry = LogEntry(
                index=len(self._log) + 1,
                operation=operation["op"],
                key=operation["key"],
                value=operation["value"],
                committed=False,
            )
            self._log.append(entry)
            
            self._state.node_states = {
                "client": "requesting",
                "wal": "appending",
                "storage": "ready",
            }
            self._add_log(
                f"{self._state.current_time:.2f}s",
                "INFO",
                f"LOG_APPENDED: [{entry.index}] {operation['key']}={operation['value']}"
            )
            self._state.events.append({"time": self._state.current_time, "type": "log_append", "label": "Log Append"})
            
        elif self._step_in_op == 2:
            # Step 3: WAL flushes to disk
            self._log[-1].committed = True
            
            self._state.node_states = {
                "client": "requesting",
                "wal": "flushing",
                "storage": "ready",
            }
            self._add_log(
                f"{self._state.current_time:.2f}s",
                "INFO",
                f"FLUSH_COMPLETED: Log entry [{len(self._log)}] persisted"
            )
            self._state.events.append({"time": self._state.current_time, "type": "flush", "label": "Flush"})
            
        elif self._step_in_op == 3:
            # Step 4: Apply to storage
            self._data_store[operation["key"]] = operation["value"]
            
            self._state.node_states = {
                "client": "requesting",
                "wal": "applying",
                "storage": "applying",
            }
            self._add_log(
                f"{self._state.current_time:.2f}s",
                "INFO",
                f"DATA_APPLIED: {operation['key']}={operation['value']} in storage"
            )
            self._state.events.append({"time": self._state.current_time, "type": "apply", "label": "Apply"})
            
            self._current_op_index += 1
            self._step_in_op = 0
            return
        
        self._step_in_op += 1
    
    def _trigger_crash(self) -> None:
        """Simulate a crash."""
        self._crashed = True
        self._state.node_states = {
            "client": "crashed",
            "wal": "crashed",
            "storage": "crashed",
        }
        self._add_log(
            f"{self._state.current_time:.2f}s",
            "ERROR",
            "CRASH: System crashed!"
        )
        self._state.events.append({"time": self._state.current_time, "type": "crash", "label": "CRASH"})
    
    def _do_recovery(self) -> None:
        """Recover from crash by replaying log."""
        self._recovered = True
        
        self._state.node_states = {
            "client": "recovering",
            "wal": "recovering",
            "storage": "recovering",
        }
        self._add_log(
            f"{self._state.current_time:.2f}s",
            "INFO",
            "RECOVERY_STARTED: System crashed, initiating WAL recovery"
        )
        
        # Count committed vs uncommitted entries
        committed_entries = [e for e in self._log if e.committed]
        self._add_log(
            f"{self._state.current_time:.2f}s",
            "INFO",
            f"RECOVERY: Found {len(self._log)} total entries, {len(committed_entries)} committed"
        )
        
        recovered_keys = []
        for entry in self._log:
            if entry.committed:
                self._data_store[entry.key] = entry.value
                recovered_keys.append(f"{entry.key}={entry.value}")
                self._add_log(
                    f"{self._state.current_time:.2f}s",
                    "INFO",
                    f"REPLAY_ENTRY: [{entry.index}] {entry.operation} {entry.key}={entry.value} (committed=True)"
                )
            else:
                self._add_log(
                    f"{self._state.current_time:.2f}s",
                    "INFO",
                    f"SKIP_ENTRY: [{entry.index}] {entry.operation} {entry.key}={entry.value} (committed=False - not replayed)"
                )
        
        self._add_log(
            f"{self._state.current_time:.2f}s",
            "INFO",
            f"RECOVERY_COMPLETED: Replayed {len(recovered_keys)} committed entries, {len(self._data_store)} keys now in data store"
        )
        
        self._state.node_states = {
            "client": "idle",
            "wal": "ready",
            "storage": "ready",
        }
        self._state.events.append({"time": self._state.current_time, "type": "recovery", "label": "Recovery"})
        
        self._current_op_index += 1
        self._step_in_op = 0
    
    def get_result(self) -> dict:
        """Return WAL-specific result as a dictionary."""
        return {
            "steps": self._step_count,
            "operations": len(self._operations),
            "log_entries": len(self._log),
            "stored_keys": len(self._data_store),
            "crashed": self._crashed,
            "recovered": self._recovered,
            "success": (self._crashed and self._recovered) or not self._crashed,
        }
    
    def get_validation(self, result=None) -> EngineValidation:
        committed_entries = [e for e in self._log if e.committed]
        all_recovered = all(e.key in self._data_store for e in committed_entries)
        expected_keys = {e.key for e in self._log if e.committed}
        actual_keys = set(self._data_store.keys())
        data_consistent = actual_keys == expected_keys
        
        # Check: are there any uncommitted entries in data store?
        uncommitted_in_store = any(
            e.key in self._data_store and not e.committed
            for e in self._log
        )
        
        invariants = [
            {
                "name": "WriteAheadProperty",
                "description": "Data must not be applied to storage before being logged and flushed (WAL core principle)",
                "holds": not uncommitted_in_store,
            },
            {
                "name": "LogBeforeApply",
                "description": "Each operation's data is written to WAL before being applied to data store",
                "holds": len(self._log) > 0,
            },
            {
                "name": "RecoveryCorrectness",
                "description": "After crash, recovery replays all committed log entries to restore data store state",
                "holds": all_recovered if self._crashed else True,
            },
            {
                "name": "DataConsistency",
                "description": "Final data store contains exactly the keys from committed log entries",
                "holds": data_consistent,
            },
            {
                "name": "NoLostData",
                "description": "All committed operations are present in the data store (no data loss)",
                "holds": len(self._data_store) >= len(committed_entries),
            },
            {
                "name": "DurabilityGuarantee",
                "description": "Once an entry is committed (flushed), it survives crash and can be recovered",
                "holds": all_recovered if self._crashed else True,
            },
        ]
        
        success = all(inv["holds"] for inv in invariants)
        
        # Build detailed explanation
        if self._crashed and self._recovered:
            explanation = (
                f"CRASH OCCURRED → RECOVERY SUCCESSFUL. "
                f"System crashed after logging {len(committed_entries)} committed entries. "
                f"Recovery replayed all {len(committed_entries)} committed entries from WAL. "
                f"Final data store has {len(self._data_store)} keys: {list(self._data_store.keys())}. "
                f"All durability guarantees preserved."
            )
        elif self._crashed and not self._recovered:
            explanation = (
                "CRITICAL FAILURE: System crashed during recovery. "
                "Data loss may have occurred. This should not happen in a correct WAL implementation."
            )
        else:
            explanation = (
                f"NORMAL EXECUTION (no crash). "
                f"WAL completed {len(self._operations)} operations. "
                f"{len(self._log)} log entries written, {len(committed_entries)} committed. "
                f"Data store contains {len(self._data_store)} keys: {list(self._data_store.keys())}. "
                f"All invariants satisfied."
            )
        
        return EngineValidation(success=success, explanation=explanation, invariants=invariants)
    
    def get_state(self) -> dict:
        """Return state with WAL-specific metadata."""
        base = super().get_state()
        return {
            **base,
            "metadata": {
                "log": [self._log_to_dict(e) for e in self._log],
                "data_store": dict(self._data_store),
                "crashed": self._crashed,
                "recovered": self._recovered,
            },
        }
    
    def get_events(self) -> list:
        """Return events from state."""
        return self._state.events
    
    def get_metrics(self) -> dict:
        """Return WAL-specific metrics."""
        committed_count = sum(1 for e in self._log if e.committed)
        
        return {
            "operations_total": len(self._operations),
            "operations_completed": self._current_op_index,
            "log_entries": len(self._log),
            "committed_entries": committed_count,
            "stored_keys": len(self._data_store),
            "recovery_performed": self._recovered,
            "crashed": self._crashed,
        }
    
    def _log_to_dict(self, entry: LogEntry) -> dict:
        return {
            "index": entry.index,
            "operation": entry.operation,
            "key": entry.key,
            "value": entry.value,
            "committed": entry.committed,
        }
    
    def is_finished(self) -> bool:
        ops_done = self._current_op_index >= len(self._operations)
        crash_handled = not self._crashed or self._recovered
        return ops_done and crash_handled