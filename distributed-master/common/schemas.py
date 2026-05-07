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
    workerId: int
    latency: float
    success: bool = True
    
@dataclass
class WorkerStatus:
    id: int
    isAlive: bool = True
    activeTasks: int = 0