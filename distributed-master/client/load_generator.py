import asyncio
import time
from common.schemas import Request


async def runLoadTestAsync(scheduler, numberOfClients=1000):
    print(f"[CLIENT] Starting load test with {numberOfClients} clients")

    startTime = time.time()
    tasks = []

    for i in range(numberOfClients):
        request = Request(
            id=i,
            query=f"Request from client {i}"
        )

        tasks.append(scheduler.handleRequestAsync(request))

    responses = await asyncio.gather(*tasks)

    totalTime = time.time() - startTime
    successful = sum(response.success for response in responses)
    failed = len(responses) - successful
    averageLatency = (
        sum(response.latency for response in responses) / len(responses)
        if responses else 0
    )
    throughput = len(responses) / totalTime if totalTime > 0 else 0

    print("\n=== Load Test Results ===")
    print("Total Requests:", len(responses))
    print("Successful:", successful)
    print("Failed:", failed)
    print("Average Latency:", round(averageLatency, 4))
    print("Total Time:", round(totalTime, 4))
    print("Throughput:", round(throughput, 2), "req/sec")

    return responses


def runLoadTest(scheduler, numberOfClients=1000):
    return asyncio.run(runLoadTestAsync(scheduler, numberOfClients))