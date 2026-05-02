import threading
import uuid
import time


def generate_request_id():
    return str(uuid.uuid4())


def current_time():
    return time.time()


def calculate_latency(start_time):
    return time.time() - start_time


def log(message):
    print(f"[LOG] {message}")


class Request:
    def __init__(self, client_id, query):
        self.request_id = generate_request_id()
        self.client_id = client_id
        self.query = query


class Response:
    def __init__(self, request_id, result, latency):
        self.request_id = request_id
        self.result = result
        self.latency = latency

    def __str__(self):
        return f"Request ID: {self.request_id}, Result: {self.result}, Latency: {self.latency:.4f}s"


class Client:
    def __init__(self, client_id):
        self.client_id = client_id

    def create_request(self):
        query = f"request from client {self.client_id}"
        return Request(self.client_id, query)

    def send_request(self, destination):
        request = self.create_request()
        start_time = current_time()
        result = destination(request)
        latency = calculate_latency(start_time)

        response = Response(request.request_id, result, latency)

        log(f"Client {self.client_id} received: {response}")


def run_load_test(destination, number_of_clients=1000):
    clients = []
    threads = []

    for i in range(number_of_clients):
        client = Client(i)
        clients.append(client)

    for client in clients:
        t = threading.Thread(target=client.send_request, args=(destination,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
       
       
def fake_master(request):
    return f"processed {request.query}"

run_load_test(fake_master, 1000)