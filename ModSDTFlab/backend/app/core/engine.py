"""
Core execution engine base class and registry.

Architecture:
- AlgorithmEngine: Base class defining the interface for all algorithm engines.
- AlgorithmRegistry: Maps algorithm IDs to engine classes.
- Each engine subclass implements algorithm-specific logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EngineState:
    """Current state of the execution engine."""
    current_time: float = 0.0
    node_states: dict = field(default_factory=dict)
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)
    events: list = field(default_factory=list)
    scenario: str = ""  # Optional scenario name for display


@dataclass
class EngineResult:
    """Final result from the algorithm execution."""
    rounds: int = 0
    decisions: int = 0
    avg_latency: float = 0.0
    success_rate: float = 0.0


@dataclass
class EngineValidation:
    """Validation results with invariants."""
    success: bool = True
    explanation: str = ""
    invariants: list = field(default_factory=list)


class AlgorithmEngine(ABC):
    """
    Base class for algorithm execution engines.
    
    REQUIRED methods (must implement):
    - initialize(node_count, config): Set up initial state
    - step(): Advance execution by one step
    - get_state(): Return current state (time, nodes, edges, events, metadata, scenario)
    - get_logs(): Return log entries up to current time
    - get_result(): Return final result (only when finished)
    - get_validation(result=None): Return validation results (only when finished)
    - is_finished(): Check if execution is complete
    
    OPTIONAL methods (can override):
    - get_metrics(): Return algorithm-specific metrics dict
    - get_events(): Return list of events (falls back to state events)
    """
    
    def __init__(self, algorithm_id: str = ""):
        self.algorithm_id = algorithm_id
        self._state = EngineState()
        self._logs = []
        self._step_count = 0
    
    def initialize(self, node_count: int = 5, config: dict = None, scenario: dict = None) -> None:
        """Initialize the engine with node count, config, and optional scenario."""
        self._state = self._create_initial_state(node_count, config or {}, scenario)
        self._logs = self._create_initial_logs()
        self._step_count = 0
    
    @abstractmethod
    def _create_initial_state(self, node_count: int, config: dict, scenario: dict = None) -> EngineState:
        """Create initial state for this algorithm."""
        pass
    
    def _create_initial_logs(self) -> list:
        """Create initial log entries."""
        return [
            {"time": "00:00:01.000", "level": "INFO", "message": "Execution started"},
            {"time": "00:00:01.500", "level": "INFO", "message": "Nodes initialized"},
        ]
    
    @abstractmethod
    def step(self) -> None:
        """Advance execution by one step."""
        pass
    
    def get_state(self) -> dict:
        """Return current execution state."""
        return {
            "current_time": self._state.current_time,
            "node_states": self._state.node_states,
            "nodes": self._state.nodes,
            "edges": self._state.edges,
            "events": self._state.events,
            "scenario": self._state.scenario,
        }
    
    def get_logs(self) -> list:
        """Return log entries up to current time."""
        return self._logs
    
    @abstractmethod
    def get_result(self):
        """Return final result (called when finished)."""
        pass
    
    @abstractmethod
    def get_validation(self, result=None):
        """Return validation results (called when finished)."""
        pass
    
    @abstractmethod
    def is_finished(self) -> bool:
        """Check if execution is complete."""
        pass
    
    # Optional methods
    
    def get_metrics(self) -> dict:
        """Return algorithm-specific metrics. Override for custom metrics."""
        return {}
    
    def get_events(self) -> list:
        """Return events. Override for custom event handling."""
        return self._state.events
    
    def _add_log(self, time: str, level: str, message: str) -> None:
        """Helper to add a log entry."""
        self._logs.append({"time": time, "level": level, "message": message})


class AlgorithmRegistry:
    """Registry mapping algorithm IDs to engine classes."""
    
    _engines: dict[str, type[AlgorithmEngine]] = {}
    
    @classmethod
    def register(cls, algo_id: str, engine_class: type[AlgorithmEngine]) -> None:
        """Register an engine class for an algorithm."""
        cls._engines[algo_id] = engine_class
    
    @classmethod
    def get(cls, algo_id: str) -> type[AlgorithmEngine] | None:
        """Get engine class by algorithm ID."""
        return cls._engines.get(algo_id)
    
    @classmethod
    def list_algorithms(cls) -> list[dict]:
        """List all registered algorithms."""
        return [
            {"id": algo_id, "engine": engine_class.__name__}
            for algo_id, engine_class in cls._engines.items()
        ]


def register(algo_id: str):
    """Decorator to register an algorithm engine."""
    def decorator(cls: type[AlgorithmEngine]):
        AlgorithmRegistry.register(algo_id, cls)
        return cls
    return decorator