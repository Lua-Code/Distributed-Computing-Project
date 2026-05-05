from common.schemas import Request, Response
from master.scheduler import Scheduler
from master.worker_manager import WorkerManager
from lb.load_balancer import LoadBalancer


class FakeWorker:
    def __init__(self, id, shouldFail=False, maxTasks=5):
        self.id = id
        self.isAlive = True
        self.activeTasks = 0
        self.maxTasks = maxTasks
        self.shouldFail = shouldFail

    def process(self, request):
        if not self.isAlive:
            raise Exception(f"Worker {self.id} is dead")

        if self.shouldFail:
            raise Exception("Simulated worker failure")

        return Response(
            id=request.id,
            result=f"Worker {self.id} processed {request.query}",
            workerId=self.id,
            latency=0,
            success=True
        )


def buildScheduler(workers):
    workerManager = WorkerManager(workers)
    loadBalancer = LoadBalancer()
    return Scheduler(loadBalancer, workerManager)


def testSuccessfulScheduling():
    workers = [
        FakeWorker(1),
        FakeWorker(2),
        FakeWorker(3)
    ]

    scheduler = buildScheduler(workers)

    for i in range(6):
        request = Request(id=i, query=f"Test request {i}")
        response = scheduler.handleRequest(request)

        assert response.success is True
        assert response.workerId in [1, 2, 3]

    metrics = scheduler.getMetrics()

    assert metrics["totalRequests"] == 6
    assert metrics["successfulRequests"] == 6
    assert metrics["failedRequests"] == 0
    assert metrics["activeTasks"] == 0

    print("testSuccessfulScheduling passed")


def testWorkerFailureRetry():
    workers = [
        FakeWorker(1, shouldFail=True),
        FakeWorker(2),
        FakeWorker(3)
    ]

    scheduler = buildScheduler(workers)

    request = Request(id=1, query="Failure test")
    response = scheduler.handleRequest(request)

    metrics = scheduler.getMetrics()

    assert response.success is True
    assert response.workerId in [2, 3]
    assert metrics["successfulRequests"] == 1
    assert metrics["failedRequests"] == 0
    assert metrics["failedTasks"] == 1
    assert metrics["statusReport"][1]["isAlive"] is False

    print("testWorkerFailureRetry passed")


def testAllWorkersFail():
    workers = [
        FakeWorker(1, shouldFail=True),
        FakeWorker(2, shouldFail=True),
        FakeWorker(3, shouldFail=True)
    ]

    scheduler = buildScheduler(workers)

    request = Request(id=1, query="All fail test")
    response = scheduler.handleRequest(request)

    metrics = scheduler.getMetrics()

    assert response.success is False
    assert response.workerId == -1
    assert metrics["successfulRequests"] == 0
    assert metrics["failedRequests"] == 1
    assert metrics["activeTasks"] == 0

    print("testAllWorkersFail passed")


def testNoAvailableWorkers():
    workers = [
        FakeWorker(1),
        FakeWorker(2)
    ]

    for worker in workers:
        worker.isAlive = False

    scheduler = buildScheduler(workers)

    request = Request(id=1, query="No workers test")
    response = scheduler.handleRequest(request)

    metrics = scheduler.getMetrics()

    assert response.success is False
    assert response.workerId == -1
    assert metrics["failedRequests"] == 1

    print("testNoAvailableWorkers passed")


if __name__ == "__main__":
    testSuccessfulScheduling()
    testWorkerFailureRetry()
    testAllWorkersFail()
    testNoAvailableWorkers()

    print("\nAll scheduler tests passed ✅")