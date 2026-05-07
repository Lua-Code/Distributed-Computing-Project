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