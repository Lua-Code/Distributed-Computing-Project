# class LoadBalancer:
#     def __init__(self):
#         self.current_index = 0

#     def selectWorker(self, workers):
#         if not workers:
#             raise Exception("No workers available")

#         worker = workers[self.current_index % len(workers)]
#         self.current_index += 1
#         return worker

import threading


class LoadBalancer:
    def __init__(self, workers, strategy="round_robin"):
        self.workers = workers
        self.strategy = strategy
        self.index = 0
        self.total_dispatched = 0
        self.lock = threading.Lock()

    def get_available_workers(self):
        return [
            w for w in self.workers
            if w.is_alive and w.current_tasks < 5
        ]

    def get_next_worker(self):
        workers = self.get_available_workers()

        if not workers:
            raise Exception("No available workers")

        if self.strategy == "round_robin":
            return self.round_robin(workers)

        elif self.strategy == "least_connections":
            return min(workers, key=lambda w: w.current_tasks)

        elif self.strategy == "load_aware":
            return min(workers, key=lambda w: w.current_tasks / 5)

        else:
            raise ValueError("Invalid strategy")

    def round_robin(self, workers):
        with self.lock:
            worker = workers[self.index % len(workers)]
            self.index += 1
        return worker

    def dispatch(self, request):
        worker = self.get_next_worker()
        self.total_dispatched += 1
        return worker.process(request)

    def get_metrics(self):
        return {
            "strategy": self.strategy,
            "total_dispatched": self.total_dispatched
        }