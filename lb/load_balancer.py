class LoadBalancer:
    def __init__(self):
        self.current_index = 0

    def selectWorker(self, workers):
        if not workers:
            raise Exception("No workers available")

        worker = workers[self.current_index % len(workers)]
        self.current_index += 1
        return worker