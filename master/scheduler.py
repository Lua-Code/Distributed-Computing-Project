from common.config import MAX_RETRIES
from common.schemas import Response
from common.utils import current_time, calculate_latency


class Scheduler:
    def __init__(self, loadBalancer, workerManager):
        self.loadBalancer = loadBalancer
        self.workerManager = workerManager

        self.activeTasks = {}
        self.completedTasks = {}
        self.failedTasks = {}

        self.totalRequests = 0
        self.successfulRequests = 0
        self.failedRequests = 0
        self.totalLatency = 0.0

    def handleRequest(self, request):
        self.totalRequests += 1
        startTime = current_time()
        latestError = None

        for attempt in range(MAX_RETRIES):
            worker = None

            try:
                worker = self.assignWorker(request)
                self.markSchedulerTaskStarted(worker, request)

                response = worker.process(request)
                response.latency = calculate_latency(startTime)
                response.workerId = worker.id
                response.success = True

                self.markSchedulerTaskCompleted(request, response)
                self.workerManager.markWorkerTaskCompleted(worker.id)

                return response

            except Exception as e:
                latestError = str(e)

                if worker is not None:
                    self.workerManager.markWorkerTaskCompleted(worker.id)
                    self.workerManager.markWorkerDead(worker.id)

                self.failedTasks[request.id] = (latestError, attempt + 1)

        self.failedRequests += 1

        return Response(
            id=request.id,
            result=f"Request failed after retries: {latestError}",
            workerId=-1,
            latency=calculate_latency(startTime),
            success=False
        )

    def assignWorker(self, request):
        availableWorkers = self.workerManager.getAvailableWorkers()

        if not availableWorkers:
            raise ValueError("No available workers to assign :(")

        return self.loadBalancer.selectWorker(availableWorkers)

    def markSchedulerTaskStarted(self, worker, request):
        self.activeTasks[request.id] = {
            "workerId": worker.id,
            "startTime": current_time(),
        }

        self.workerManager.markWorkerTaskStarted(worker.id)

    def markSchedulerTaskCompleted(self, request, response):
        self.activeTasks.pop(request.id, None)
        self.completedTasks[request.id] = response
        self.successfulRequests += 1
        self.totalLatency += response.latency

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
            "failedTasks": len(self.failedTasks),
            "averageLatency": averageLatency,
            "statusReport": self.workerManager.getStatusReport()
        }