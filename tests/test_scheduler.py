from master.scheduler import Scheduler
from master.worker_manager import WorkerManager
from lb.load_balancer import LoadBalancer
from common.schemas import Request, Response
from common.config import MAX_TASKS_PER_WORKER


class FakeWorker:
    def __init__(self, id, max_tasks=MAX_TASKS_PER_WORKER):
        self.id = id
        self.isAlive = True
        self.activeTasks = 0
        self.maxTasks = max_tasks

    def process(self, request):
        if self.id == 1 and request.id == 3:
            raise Exception("Simulated failure")
        
        return Response(
            id=request.id,
            result=f"Worker {self.id} processed: {request.query}",
            workerId=self.id,
            latency=0,
            success=True
        )


workers = [
    FakeWorker(1),
    FakeWorker(2),
    FakeWorker(3)
]

workers[0].activeTasks = 4  # Simulate worker 1 being at max capacity
workers[1].activeTasks = 2  # Simulate worker 2 being partially busy
workers[2].activeTasks = 3  # Simulate worker 3 being partially busy

worker_manager = WorkerManager(workers)
load_balancer = LoadBalancer()
scheduler = Scheduler(load_balancer, worker_manager)

for i in range(10):
    request = Request(
        id=i,
        query=f"Test request {i}"
    )

    response = scheduler.handleRequest(request)
    print(response)

print("\nMetrics:")
print(scheduler.getMetrics())