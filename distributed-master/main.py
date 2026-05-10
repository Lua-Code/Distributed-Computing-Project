import asyncio

from master.scheduler import Scheduler
from master.worker_manager import WorkerManager
from lb.load_balancer import LoadBalancer
from workers.remoteWorker import RemoteWorker
from client.load_generator import runLoadTestAsync
from common.config import WORKER_URLS


def buildSystem():
    workers = []

    for index, url in enumerate(WORKER_URLS, start=1):
        worker = RemoteWorker(
            id=index,
            url=url,
            maxTasks=5,
            timeout=60
        )
        workers.append(worker)

    workerManager = WorkerManager(workers)
    workerManager.refreshWorkerHealth()

    loadBalancer = LoadBalancer(strategy="roundRobin")
    scheduler = Scheduler(loadBalancer, workerManager)

    return scheduler


async def runSmallRemoteTest(scheduler):
    print("\n[TEST] Running small remote worker test...\n")

    responses = await runLoadTestAsync(
        scheduler,
        numberOfClients=50
    )

    print("\n=== Small Test Responses ===")
    for response in responses:
        print(
            f"Request {response.id} | "
            f"Worker {response.workerId} | "
            f"Success: {response.success} | "
            f"Latency: {response.latency:.2f}s | "
            f"Result: {response.result[:100]}"
        )


async def main():
    print("[SYSTEM] Starting Distributed Master")
    print("[SYSTEM] Loading remote GPU workers...")

    scheduler = buildSystem()

    print("\n=== Initial Worker Status ===")
    print(scheduler.workerManager.getStatusReport())

    await runSmallRemoteTest(scheduler)

    print("\n=== Final Scheduler Metrics ===")
    print(scheduler.getMetrics())


if __name__ == "__main__":
    asyncio.run(main())