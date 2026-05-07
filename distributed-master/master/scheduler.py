import asyncio
from concurrent.futures import ThreadPoolExecutor

from common.config import MAX_RETRIES
from common.schemas import Response
from common.utils import current_time, calculate_latency


class Scheduler:
    def __init__(self, loadBalancer, workerManager, maxThreads=10):
        self.loadBalancer = loadBalancer
        self.workerManager = workerManager
        self.executor = ThreadPoolExecutor(max_workers=maxThreads)

        self.activeTasks = {}
        self.completedTasks = {}
        self.failedTasks = {}

        self.totalRequests = 0
        self.successfulRequests = 0
        self.failedRequests = 0
        self.totalLatency = 0.0

        self.lock = asyncio.Lock()

    async def handleRequestAsync(self, request):
        async with self.lock:
            self.totalRequests += 1

        startTime = current_time()
        latestError = None

        for attempt in range(MAX_RETRIES):
            worker = None

            try:
                worker = await self.assignWorkerAsync()
                await self.markSchedulerTaskStarted(worker, request)

                loop = asyncio.get_running_loop()

                response = await loop.run_in_executor(
                    self.executor,
                    worker.process,
                    request
                )

                response.latency = calculate_latency(startTime)
                response.workerId = worker.id
                response.success = True

                await self.markSchedulerTaskCompleted(request, response)
                await self.markWorkerTaskCompleted(worker.id)

                return response

            except Exception as e:
                latestError = str(e)

                async with self.lock:
                    self.activeTasks.pop(request.id, None)
                    self.failedTasks[f"{request.id}-attempt-{attempt + 1}"] = latestError

                if worker is not None:
                    await self.markWorkerTaskCompleted(worker.id)
                    self.workerManager.markWorkerDead(worker.id)

        async with self.lock:
            self.failedRequests += 1

        return Response(
            id=request.id,
            result=f"Request failed after retries: {latestError}",
            workerId=-1,
            latency=calculate_latency(startTime),
            success=False
        )

    async def assignWorkerAsync(self):
        availableWorkers = self.workerManager.getAvailableWorkers()

        healthyWorkers = []

        for worker in availableWorkers:
            if hasattr(worker, "healthCheck"):
                loop = asyncio.get_running_loop()
                isHealthy = await loop.run_in_executor(
                    self.executor,
                    worker.healthCheck
                )

                if isHealthy:
                    healthyWorkers.append(worker)
                else:
                    self.workerManager.markWorkerDead(worker.id)
            else:
                healthyWorkers.append(worker)

        if not healthyWorkers:
            raise ValueError("No available workers to assign :(")

        return self.loadBalancer.selectWorker(healthyWorkers)

    async def markSchedulerTaskStarted(self, worker, request):
        async with self.lock:
            self.activeTasks[request.id] = {
                "workerId": worker.id,
                "startTime": current_time()
            }

            self.workerManager.markWorkerTaskStarted(worker.id)

    async def markSchedulerTaskCompleted(self, request, response):
        async with self.lock:
            self.activeTasks.pop(request.id, None)
            self.completedTasks[request.id] = response
            self.successfulRequests += 1
            self.totalLatency += response.latency

    async def markWorkerTaskCompleted(self, workerId):
        async with self.lock:
            self.workerManager.markWorkerTaskCompleted(workerId)

    def getMetrics(self):
        averageLatency = (
            self.totalLatency / self.successfulRequests
            if self.successfulRequests > 0
            else 0.0
        )

        return {
            "totalRequests": self.totalRequests,
            "successfulRequests": self.successfulRequests,
            "failedRequests": self.failedRequests,
            "activeTasks": len(self.activeTasks),
            "completedTasks": len(self.completedTasks),
            "failedAttempts": len(self.failedTasks),
            "averageLatency": averageLatency,
            "statusReport": self.workerManager.getStatusReport()
        }

    def handleRequest(self, request):
        try:
            loop = asyncio.get_running_loop()
            raise RuntimeError(
                "handleRequest() cannot be used inside an active event loop. "
                "Use await handleRequestAsync(request) instead."
            )
        except RuntimeError as error:
            if "no running event loop" in str(error).lower():
                return asyncio.run(self.handleRequestAsync(request))
            raise