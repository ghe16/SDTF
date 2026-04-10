"""
Execution manager - orchestrates algorithm engines.

Manages execution lifecycle:
- Create engine from registry
- Step through execution
- Track execution state
- Provide unified response format for frontend
"""

import uuid
from app.core.engine import AlgorithmEngine, AlgorithmRegistry, EngineResult


class ExecutionManager:
    """
    Manages execution instances with unified response format.
    
    Response structure:
    {
        id, algorithm, status, current_time,
        graph: { nodes, edges, node_states },
        logs: [...],
        metrics: {...},       # algorithm-specific
        validation: {...},    # if completed
        result: {...}         # if completed
    }
    """
    
    def __init__(self):
        self._executions: dict[str, dict] = {}
    
    def start(self, algorithm_id: str, node_count: int = 5, config: dict = None, scenario: dict = None) -> str:
        """Start a new execution and return execution ID."""
        engine_class = AlgorithmRegistry.get(algorithm_id)
        if not engine_class:
            raise ValueError(f"Unknown algorithm: {algorithm_id}")
        
        exec_id = str(uuid.uuid4())[:8]
        engine = engine_class()
        engine.algorithm_id = algorithm_id
        engine.initialize(node_count, config, scenario)
        
        self._executions[exec_id] = {
            "id": exec_id,
            "algorithm": algorithm_id,
            "engine": engine,
            "status": "running",
        }
        
        return exec_id
    
    def step(self, exec_id: str) -> None:
        """Advance execution by one step."""
        if exec_id not in self._executions:
            raise ValueError(f"Execution not found: {exec_id}")
        
        execution = self._executions[exec_id]
        engine = execution["engine"]
        
        if execution["status"] == "running":
            engine.step()
            
            if engine.is_finished():
                execution["status"] = "completed"
                execution["result"] = engine.get_result()
                execution["validation"] = engine.get_validation(execution["result"])
    
    def get_execution(self, exec_id: str) -> dict:
        """Get full execution data in unified format."""
        if exec_id not in self._executions:
            raise ValueError(f"Execution not found: {exec_id}")
        
        execution = self._executions[exec_id]
        engine = execution["engine"]
        state = engine.get_state()
        logs = engine.get_logs()
        
        # Build unified response
        response = {
            "id": exec_id,
            "algorithm": execution["algorithm"],
            "status": execution["status"],
            "current_time": state.get("current_time", 0),
            "scenario": state.get("scenario", ""),
            "graph": {
                "nodes": state.get("nodes", []),
                "edges": state.get("edges", []),
                "node_states": state.get("node_states", {}),
            },
            "events": self._get_engine_events(engine),
            "logs": logs,
            "metrics": self._get_engine_metrics(engine),
            "metadata": state.get("metadata", {}),
        }
        
        # Add result and validation if completed
        if execution["status"] == "completed":
            result = execution.get("result")
            validation = execution.get("validation")
            
            if result:
                response["result"] = self._serialize_result(result)
            
            if validation:
                response["validation"] = self._serialize_validation(validation)
        
        return response
    
    def _get_engine_metrics(self, engine) -> dict:
        """Get metrics from engine, with fallback for engines without get_metrics."""
        if hasattr(engine, 'get_metrics'):
            metrics = engine.get_metrics()
            if isinstance(metrics, dict):
                return metrics
        return {}
    
    def _get_engine_events(self, engine) -> list:
        """Get events from engine, with fallback to state events."""
        if hasattr(engine, 'get_events'):
            events = engine.get_events()
            if isinstance(events, list):
                return events
        # Fallback to state events for engines without get_events
        state = engine.get_state()
        return state.get("events", [])
    
    def _serialize_value(self, value) -> dict:
        """Serialize a value safely to dict."""
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        if hasattr(value, 'model_dump'):
            return value.model_dump()
        if hasattr(value, 'dict'):
            return value.dict()
        if hasattr(value, '__dict__'):
            return vars(value)
        return value
    
    def _serialize_result(self, result) -> dict:
        """Serialize result object to dict."""
        return self._serialize_value(result)
    
    def _serialize_validation(self, validation) -> dict:
        """Serialize validation object to dict."""
        return self._serialize_value(validation)
    
    def get_state(self, exec_id: str) -> dict:
        """Get execution state (legacy compatibility)."""
        return self.get_execution(exec_id)
    
    def get_logs(self, exec_id: str) -> list:
        """Get execution logs (legacy compatibility)."""
        if exec_id not in self._executions:
            raise ValueError(f"Execution not found: {exec_id}")
        return self._executions[exec_id]["engine"].get_logs()
    
    def get_result(self, exec_id: str) -> dict:
        """Get execution result (legacy compatibility)."""
        exec_data = self.get_execution(exec_id)
        if exec_data["status"] != "completed" or "result" not in exec_data:
            return {"status": "running", "result": None}
        
        result = exec_data["result"]
        serialized = self._serialize_result(result)
        return {
            "id": exec_id,
            "algorithm": exec_data["algorithm"],
            **serialized,
        }
    
    def get_validation(self, exec_id: str) -> dict:
        """Get execution validation (legacy compatibility)."""
        exec_data = self.get_execution(exec_id)
        if "validation" not in exec_data:
            return None
        return {"validation": exec_data["validation"]}
    
    def list(self) -> list:
        """List all executions."""
        return [
            {"id": e["id"], "algorithm": e["algorithm"], "status": e["status"]}
            for e in self._executions.values()
        ]


# Global manager instance
manager = ExecutionManager()