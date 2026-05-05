import time
from common.config import USE_REAL_LLM, USE_RAG, SIMULATED_PROCESSING_TIME
from common.schemas import Response


class TaskExecutor:
    def __init__(self, workerId):
        self.workerId = workerId
        self.llm = None

        if USE_REAL_LLM:
            from llm.inference import LLM
            self.llm = LLM()

    def execute(self, request):
        startTime = time.time()

        if USE_REAL_LLM:
            context = ""

            if USE_RAG:
                from rag.retriever import retrieveContext
                context = retrieveContext(request.query)

            result = self.llm.generate(request.query, context)

        else:
            time.sleep(SIMULATED_PROCESSING_TIME)
            result = f"Simulated LLM response for: {request.query}"

        latency = time.time() - startTime

        return Response(
            id=request.id,
            result=result,
            workerId=self.workerId,
            latency=latency,
            success=True
        )