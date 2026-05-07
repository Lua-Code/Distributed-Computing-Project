import time
import asyncio

from common.schemas import Request
from master.scheduler import Scheduler
from master.worker_manager import WorkerManager
from lb.load_balancer import LoadBalancer
from workers.worker import Worker

from rag.ingestion import ingestDocuments
from rag.vector_store import vectorStore


# ---------------- RAG SETUP ----------------
def setupRag():
    loaded = vectorStore.load()

    if loaded:
        print("[RAG] Loaded existing VectorDB")
        return

    print("[RAG] No VectorDB found → ingesting...")

    documents = [
        "Load balancing distributes requests across workers.",
        "Fault tolerance retries failed tasks on healthy workers.",
        "RAG retrieves relevant context for LLM responses.",
        "Scheduler assigns tasks and monitors workers.",
        "Workers process requests in parallel."
    ]

    ingestDocuments(documents)
    print("[RAG] Ingestion complete")


# ---------------- SYSTEM SETUP ----------------
def buildSystem():
    workers = [
        Worker(id=1),
        Worker(id=2),
        Worker(id=3)
    ]

    workerManager = WorkerManager(workers)
    loadBalancer = LoadBalancer()
    scheduler = Scheduler(loadBalancer, workerManager)

    return scheduler


# ---------------- FAILURE SIMULATION ----------------
async def simulateWorkerFailure(scheduler, workerId=1, delay=2):
    await asyncio.sleep(delay)

    worker = scheduler.workerManager.getWorkerById(workerId)
    worker.fail()

    print(f"\n[FAILURE] Worker {workerId} FAILED mid-test\n")


# ---------------- CONCURRENT TEST ----------------
async def runConcurrentTest(scheduler, numberOfRequests=20):
    print(f"\n[TEST] Running {numberOfRequests} concurrent requests...\n")

    startTime = time.time()
    tasks = []

    for i in range(numberOfRequests):
        request = Request(
            id=i,
            query=f"Concurrent request {i}"
        )

        tasks.append(scheduler.handleRequestAsync(request))

    # 🔥 simulate failure during execution
    failureTask = asyncio.create_task(
        simulateWorkerFailure(scheduler, workerId=1, delay=2)
    )

    responses = await asyncio.gather(*tasks)
    await failureTask

    totalTime = time.time() - startTime

    print("\n==================== RESULTS ====================")

    for r in responses:
        print(
            f"Request {r.id} | Worker {r.workerId} | "
            f"Success: {r.success} | Latency: {r.latency:.2f}s"
        )

    success = sum(r.success for r in responses)
    failed = len(responses) - success
    throughput = len(responses) / totalTime if totalTime > 0 else 0

    print("\n==================== SUMMARY ====================")
    print("Total Requests:", len(responses))
    print("Successful:", success)
    print("Failed:", failed)
    print("Total Time:", round(totalTime, 2), "sec")
    print("Throughput:", round(throughput, 2), "req/sec")

    print("\n==================== METRICS ====================")
    print(scheduler.getMetrics())


# ---------------- MAIN ----------------
def main():
    print("[SYSTEM] Starting Distributed System Test")

    setupRag()
    scheduler = buildSystem()

    asyncio.run(runConcurrentTest(scheduler, numberOfRequests=20))


if __name__ == "__main__":
    main()