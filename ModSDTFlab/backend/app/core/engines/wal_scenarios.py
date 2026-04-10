"""
WAL Scenarios - Predefined test cases for Write-Ahead Logging

Each scenario defines:
- operations: list of operations to execute
- crash: when/how to crash (None = no crash)
- description: human-readable explanation
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class WALScenario:
    """Definition of a WAL test scenario."""
    name: str
    description: str
    operations: list[dict]
    crash_step: Optional[int] = None  # Step number to crash at (None = no crash)


SCENARIOS = {
    "normal_write": WALScenario(
        name="normal_write",
        description="Single write operation completes normally",
        operations=[
            {"op": "SET", "key": "counter", "value": "1"},
        ],
        crash_step=None,
    ),
    
    "crash_after_log": WALScenario(
        name="crash_after_log",
        description="Crash after log append, then recover from WAL",
        operations=[
            {"op": "SET", "key": "balance", "value": "100"},
        ],
        crash_step=3,  # After FLUSH_COMPLETED, before DATA_APPLIED
    ),
    
    "multiple_operations": WALScenario(
        name="multiple_operations",
        description="Multiple sequential operations to demonstrate batching",
        operations=[
            {"op": "SET", "key": "x", "value": "10"},
            {"op": "SET", "key": "y", "value": "20"},
            {"op": "SET", "key": "z", "value": "x+y"},
        ],
        crash_step=None,
    ),
    
    "crash_after_first": WALScenario(
        name="crash_after_first",
        description="Crash after first of multiple operations",
        operations=[
            {"op": "SET", "key": "a", "value": "1"},
            {"op": "SET", "key": "b", "value": "2"},
            {"op": "SET", "key": "c", "value": "3"},
        ],
        crash_step=3,  # Crash after first operation is logged/flushed
    ),
    
    "sequential_crashes": WALScenario(
        name="sequential_crashes",
        description="Multiple crashes and recoveries",
        operations=[
            {"op": "SET", "key": "order", "value": "1"},
            {"op": "SET", "key": "order", "value": "2"},
        ],
        crash_step=3,  # Crash after first completes
    ),
}


def get_scenario(name: str) -> Optional[WALScenario]:
    """Get scenario by name, or None if not found."""
    return SCENARIOS.get(name)


def list_scenarios() -> list[dict]:
    """List all available scenarios."""
    return [
        {"id": s.name, "description": s.description}
        for s in SCENARIOS.values()
    ]