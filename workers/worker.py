from workers.task_executor import TaskExecutor


class Worker:
    def __init__(self, id, maxTasks=5):
        self.id = id
        self.isAlive = True
        self.activeTasks = 0
        self.maxTasks = maxTasks
        self.taskExecutor = TaskExecutor(id)

    def process(self, request):
        if not self.isAlive:
            raise Exception(f"Worker {self.id} is down")

        print(f"[Worker {self.id}] Processing request {request.id}")
        return self.taskExecutor.execute(request)

    def fail(self):
        self.isAlive = False

    def recover(self):
        self.isAlive = True
        self.activeTasks = 0