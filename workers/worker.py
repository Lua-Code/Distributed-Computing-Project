class GPUWorker:
    def __init__(self, id, maxTasks=5):
        self.id = id
        self.isAlive = True
        self.activeTasks = 0
        self.maxTasks = maxTasks

    # Simulate processing a request meow meow
    def process(self, request):
        return f"Worker {self.id} processed request {request.id}"