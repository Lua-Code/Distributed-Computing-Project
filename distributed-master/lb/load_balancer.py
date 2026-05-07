class LoadBalancer:
    def __init__(self, strategy="roundRobin"):
        self.strategy = strategy
        self.currentIndex = 0

    def selectWorker(self, workers):
        if not workers:
            raise ValueError("No workers available")

        if self.strategy == "leastConnections":
            return min(workers, key=lambda worker: worker.activeTasks)

        worker = workers[self.currentIndex % len(workers)]
        self.currentIndex += 1
        return worker