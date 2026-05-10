import time
import uvicorn

from fastapi import FastAPI
from pydantic import BaseModel

from workers.worker import Worker
from common.config import USE_REAL_LLM


app = FastAPI(title="GPU Worker Node")

worker = Worker(id=1)


class ProcessRequest(BaseModel):
    id: int
    query: str


class ProcessResponse(BaseModel):
    id: int
    result: str
    workerId: int
    latency: float
    success: bool


@app.on_event("startup")
def startupEvent():
    print("[SERVER] Starting GPU Worker Server...")

    if USE_REAL_LLM:
        print("[SERVER] Initializing LLM at startup...")

        # Forces TaskExecutor / LLM to initialize before first request
        worker.taskExecutor.initialize()

        print("[SERVER] LLM initialized successfully")

    print("[SERVER] Worker server ready")


@app.get("/health")
def healthCheck():
    return {
        "status": "alive",
        "workerId": worker.id,
        "isAlive": worker.isAlive,
        "activeTasks": worker.activeTasks,
        "maxTasks": worker.maxTasks,
        "llmLoaded": worker.taskExecutor.isLlmLoaded()
    }


@app.post("/process", response_model=ProcessResponse)
def processRequest(request: ProcessRequest):
    startTime = time.time()

    try:
        response = worker.process(request)

        return ProcessResponse(
            id=response.id,
            result=response.result,
            workerId=response.workerId,
            latency=response.latency,
            success=response.success
        )

    except Exception as e:
        return ProcessResponse(
            id=request.id,
            result=f"Worker failed: {str(e)}",
            workerId=worker.id,
            latency=time.time() - startTime,
            success=False
        )


@app.post("/fail")
def failWorker():
    worker.fail()
    return {
        "message": f"Worker {worker.id} failed",
        "isAlive": worker.isAlive
    }


@app.post("/recover")
def recoverWorker():
    worker.recover()
    return {
        "message": f"Worker {worker.id} recovered",
        "isAlive": worker.isAlive
    }


if __name__ == "__main__":
    uvicorn.run(
        "worker_server:app",
        host="0.0.0.0",
        port=8001,
        reload=False
    )