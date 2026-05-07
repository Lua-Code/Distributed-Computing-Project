from common.config import MAX_TASKS_PER_WORKER


class WorkerManager:
    def __init__(self, workers):
        self.workers = {worker.id: worker for worker in workers}

    def getWorkerById(self, workerId):
        if workerId not in self.workers:
            raise ValueError(f"Worker with ID {workerId} not found")
        return self.workers[workerId]

    def getAllWorkers(self):
        return list(self.workers.values())

    def refreshWorkerHealth(self):
        for worker in self.workers.values():
            if hasattr(worker, "healthCheck"):
                worker.healthCheck()

    def getAliveWorkers(self):
        return [
            worker for worker in self.workers.values()
            if worker.isAlive
        ]

    def getAvailableWorkers(self):
        return [
            worker for worker in self.getAliveWorkers()
            if worker.activeTasks < worker.maxTasks
        ]

    def markWorkerTaskStarted(self, workerId):
        worker = self.getWorkerById(workerId)
        worker.activeTasks += 1

    def markWorkerTaskCompleted(self, workerId):
        worker = self.getWorkerById(workerId)
        if worker.activeTasks > 0:
            worker.activeTasks -= 1

    def markWorkerDead(self, workerId):
        worker = self.getWorkerById(workerId)
        worker.isAlive = False
        worker.activeTasks = 0

    def reviveWorker(self, workerId):
        worker = self.getWorkerById(workerId)
        worker.isAlive = True
        worker.activeTasks = 0

    def getWorkerLoad(self, workerId):
        worker = self.getWorkerById(workerId)
        return worker.activeTasks

    def hasAvailableWorkers(self):
        return len(self.getAvailableWorkers()) > 0

    def getStatusReport(self):
        return {
            worker.id: {
                "url": getattr(worker, "url", "local"),
                "isAlive": worker.isAlive,
                "activeTasks": worker.activeTasks,
                "maxTasks": worker.maxTasks
            }
            for worker in self.workers.values()
        }

    def resetWorkers(self):
        for worker in self.workers.values():
            worker.isAlive = True
            worker.activeTasks = 0