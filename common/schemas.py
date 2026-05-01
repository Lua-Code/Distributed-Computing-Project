from dataclasses import dataclass
import time

@dataclass
class Request:
    id: int
    query: str
    timestamp: float = time.time()

@dataclass
class Response:
    id: int
    result: str
    worker_id: int
    latency: float
    success: bool = True
    
@dataclass
class WorkerStatus:
    id: int
    is_alive: bool = True
    active_tasks: int = 0