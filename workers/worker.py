import time
from llm.inference import run_llm
from rag.retriever import retrieve_context
from common.schemas import Response


class Worker:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.is_alive = True
        self.current_tasks = 0

    def process(self, request):
        if not self.is_alive:
            raise Exception(f"Worker {self.worker_id} is down")

        self.current_tasks += 1
        start_time = time.time()

        try:
            print(f"[Worker {self.worker_id}] Processing request {request.id}")

            context = retrieve_context(request.query)
            result = run_llm(request.query, context)

            latency = time.time() - start_time

            return Response(
                id=request.id,
                result=result,
                latency=latency
            )

        finally:
            self.current_tasks -= 1

    def fail(self):
        self.is_alive = False

    def recover(self):
        self.is_alive = True