from fastapi import APIRouter

router = APIRouter()

ALGORITHMS = [
    {"id": "paxos", "name": "Paxos", "description": "Classic consensus algorithm for fault-tolerant distributed systems"},
    {"id": "raft", "name": "Raft", "description": "Leader-based consensus with log replication"},
    {"id": "etcd", "name": "etcd", "description": "Distributed key-value store implementing Raft"},
    {"id": "ot", "name": "Operational Transform", "description": "Conflict resolution for collaborative editing"},
    {"id": "crdt", "name": "CRDT", "description": "Conflict-free replicated data types for eventual consistency"},
    {"id": "wal", "name": "WAL", "description": "Write-Ahead Logging for durability and crash recovery"},
    {"id": "2pc", "name": "2PC", "description": "Two-Phase Commit for distributed transactions"},
    {"id": "3pc", "name": "3PC", "description": "Three-Phase Commit with improved failure handling"},
    {"id": "gossip", "name": "Gossip Protocol", "description": "Epidemic broadcast for scalable peer-to-peer systems"},
    {"id": "primary-backup", "name": "Primary-Backup", "description": "Simple primary-backup replication model"},
    {"id": "leader-election", "name": "Leader Election", "description": "Dynamic leader selection for cluster coordination"},
]

# Registry mapping algorithm IDs to engine classes
# Populated at runtime from core engine registry
ALGORITHM_REGISTRY: dict[str, type] = {}


def get_algorithm_class(algo_id: str) -> type:
    """
    Get the engine class for an algorithm.
    
    Args:
        algo_id: Algorithm identifier
        
    Returns:
        Engine class for the algorithm
        
    Raises:
        ValueError: If algorithm is not registered
    """
    # Import here to avoid circular imports
    from app.core.engine import AlgorithmRegistry
    
    engine_class = AlgorithmRegistry.get(algo_id)
    if engine_class is None:
        raise ValueError(f"No engine registered for algorithm: {algo_id}")
    return engine_class


def refresh_registry() -> None:
    """Refresh ALGORITHM_REGISTRY from the core engine registry."""
    from app.core.engine import AlgorithmRegistry
    
    global ALGORITHM_REGISTRY
    for algo_id in [a["id"] for a in ALGORITHMS]:
        engine_class = AlgorithmRegistry.get(algo_id)
        if engine_class:
            ALGORITHM_REGISTRY[algo_id] = engine_class


@router.get("/algorithms")
def list_algorithms():
    return ALGORITHMS


@router.get("/algorithms/{algo_id}")
def get_algorithm(algo_id: str):
    for algo in ALGORITHMS:
        if algo["id"] == algo_id:
            return algo
    return {"error": "Not found"}