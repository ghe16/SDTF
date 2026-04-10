from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.manager import manager

router = APIRouter()


class StartExecutionRequest(BaseModel):
    algorithm: str
    node_count: int = 5
    config: Optional[dict] = None
    scenario: Optional[str] = None


@router.post("/executions/start")
def start_execution(req: StartExecutionRequest):
    """Start a new execution for the specified algorithm."""
    try:
        exec_id = manager.start(req.algorithm, req.node_count, req.config, req.scenario)
        return {"id": exec_id, "status": "running"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/executions/{exec_id}/state")
def get_execution_state(exec_id: str):
    """Get current state of an execution."""
    try:
        return manager.get_state(exec_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Execution not found")


@router.get("/executions/{exec_id}/logs")
def get_execution_logs(exec_id: str):
    """Get logs for an execution."""
    try:
        return {"logs": manager.get_logs(exec_id)}
    except ValueError:
        raise HTTPException(status_code=404, detail="Execution not found")


@router.get("/executions/{exec_id}/result")
def get_execution_result(exec_id: str):
    """Get result of a completed execution."""
    try:
        return manager.get_result(exec_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Execution not found")


@router.get("/executions/{exec_id}/validation")
def get_execution_validation(exec_id: str):
    """Get validation results of a completed execution."""
    try:
        validation = manager.get_validation(exec_id)
        if validation is None:
            return {"status": "running", "validation": None}
        return {"validation": validation}
    except ValueError:
        raise HTTPException(status_code=404, detail="Execution not found")


@router.post("/executions/{exec_id}/step")
def step_execution(exec_id: str):
    """Step an execution forward by one step (for manual stepping)."""
    try:
        manager.step(exec_id)
        return {"status": "ok"}
    except ValueError:
        raise HTTPException(status_code=404, detail="Execution not found")


@router.post("/executions/{exec_id}/run")
def run_execution(exec_id: str):
    """Run execution until completion or max steps reached."""
    try:
        history = []
        # Step until finished (max 20 steps to prevent infinite loop)
        for _ in range(20):
            manager.step(exec_id)
            state = manager.get_state(exec_id)
            history.append(state)
            if state["status"] != "running":
                break
        
        return {"status": "completed", "history": history}
    except ValueError:
        raise HTTPException(status_code=404, detail="Execution not found")


@router.get("/executions")
def list_executions():
    """List all executions."""
    return {"executions": manager.list()}