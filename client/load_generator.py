import threading
import time
from common.schemas import Request


def log(message):
    print(f"[LOG] {message}")


class Client:
    def __init__(self, clientId):
        self.clientId = clientId

    def createRequest(self):
        query = f"request from client {self.clientId}"
        return Request(id=self.clientId, query=query)

    def sendRequest(self, scheduler, results):
        request = self.createRequest()

        startTime = time.time()
        response = scheduler.handleRequest(request)
        latency = time.time() - startTime

        response.latency = latency
        results.append(response)

        log(f"Client {self.clientId} received: {response.result}")


def runLoadTest(scheduler, numberOfClients=1000):
    clients = []
    threads = []
    results = []

    for i in range(numberOfClients):
        clients.append(Client(i))

    for client in clients:
        t = threading.Thread(
            target=client.sendRequest,
            args=(scheduler, results)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # metrics
    success = sum(r.success for r in results)
    total = len(results)
    avgLatency = sum(r.latency for r in results) / total if total else 0

    print("\n=== Load Test Results ===")
    print("Total:", total)
    print("Success:", success)
    print("Failed:", total - success)
    print("Avg Latency:", avgLatency)