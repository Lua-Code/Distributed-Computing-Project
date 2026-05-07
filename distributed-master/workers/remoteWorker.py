import requests
from common.schemas import Response


class RemoteWorker:
    def __init__(self, id, url, maxTasks=5, timeout=60):
        self.id = id
        self.url = url.rstrip("/")
        self.maxTasks = maxTasks
        self.timeout = timeout

        self.isAlive = True
        self.activeTasks = 0

    def healthCheck(self):
        try:
            response = requests.get(
                f"{self.url}/health",
                timeout=3
            )

            if response.status_code != 200:
                self.isAlive = False
                return False

            data = response.json()

            self.isAlive = data.get("status") == "alive"
            self.activeTasks = data.get("activeTasks", self.activeTasks)
            self.maxTasks = data.get("maxTasks", self.maxTasks)

            return self.isAlive

        except Exception:
            self.isAlive = False
            return False

    def process(self, request):
        if not self.isAlive:
            raise Exception(f"Remote worker {self.id} is down")

        payload = {
            "id": request.id,
            "query": request.query
        }

        try:
            response = requests.post(
                f"{self.url}/process",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code != 200:
                raise Exception(f"Worker returned HTTP {response.status_code}")

            data = response.json()

            if not data.get("success"):
                raise Exception(data.get("result", "Remote worker failed"))

            return Response(
                id=data["id"],
                result=data["result"],
                workerId=self.id,
                latency=data["latency"],
                success=data["success"]
            )

        except Exception as e:
            self.isAlive = False
            raise Exception(f"Remote worker {self.id} failed: {str(e)}")

    def fail(self):
        try:
            requests.post(
                f"{self.url}/fail",
                timeout=3
            )
        except Exception:
            pass

        self.isAlive = False

    def recover(self):
        try:
            response = requests.post(
                f"{self.url}/recover",
                timeout=3
            )

            if response.status_code != 200:
                self.isAlive = False
                return False

            return self.healthCheck()

        except Exception:
            self.isAlive = False
            return False