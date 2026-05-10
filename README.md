# Distributed AI Inference System

## Overview

This project is a distributed AI inference system designed to simulate large-scale AI workload processing using remote GPU worker nodes.

The system separates the master node from GPU worker nodes to emulate a realistic distributed computing environment.

The README focuses on setup, execution, configuration, testing, and scaling procedures.

---

# Features

- Distributed architecture
- Remote GPU worker nodes
- Async task scheduling
- Concurrent request handling
- Load balancing
- Fault tolerance and retries
- Retrieval-Augmented Generation (RAG)
- FAISS Vector Database
- Scalable multi-worker support
- HTTP-based worker communication

---

# System Architecture

```text
Client Requests
   ↓
Master Scheduler
   ↓
Load Balancer
   ↓ HTTP
Remote GPU Worker Nodes
   ↓
RAG + LLM Inference
   ↓
Response Returned
````

---

# Project Structure

```text
root/
├── distributed-master/
│   ├── client/
│   ├── common/
│   ├── lb/
│   ├── master/
│   ├── workers/
│   ├── tests/
│   └── main.py
│
├── gpu-worker/
│   ├── common/
│   ├── llm/
│   ├── rag/
│   ├── workers/
│   ├── data/
│   ├── tests/
│   └── worker_server.py
│
├── .venv/
└── requirements.txt
```

---

# Requirements

## Python Version

Python 3.10 or newer is recommended.

---

# Installation

## 1. Clone the Repository

(Skip if using downloaded files)

```bash
git clone https://github.com/Lua-Code/Distributed-Computing-Project
cd Distributed-Computing-Project
```

---

## 2. Create Shared Virtual Environment

The entire project uses:

* one shared virtual environment
* one shared requirements file

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs dependencies for:

* distributed-master
* gpu-worker

---

# Running the System

The system requires:

* one machine running the distributed master node
* at least one machine running a GPU worker node

All machines must be connected to the same network unless VPN tunneling or external networking solutions are configured.

---

# Worker Node Setup

## Step 1: Start Worker Server

On the worker machine:

```bash
cd gpu-worker
python worker_server.py
```

Expected output:

```text
Uvicorn running on http://0.0.0.0:8001
```

---

## Step 2: Find Worker IP Address

### Windows

```bash
ipconfig
```

Locate:

```text
IPv4 Address
```

Example:

```text
192.168.1.25
```

---

# Master Node Configuration

Open:

```text
distributed-master/common/config.py
```

Update:

```python
WORKER_URLS = [
    "http://WORKER_1_IP_ADDRESS:8001"
]
```

Additional workers can be added:

```python
WORKER_URLS = [
    "http://WORKER_1_IP_ADDRESS:8001",
    "http://WORKER_2_IP_ADDRESS:8001",
    "http://WORKER_3_IP_ADDRESS:8001"
]
```

---

# Verify Worker Health

From another machine/browser:

```text
http://<worker-ip>:8001/health
```

Example:

```text
http://192.168.1.25:8001/health
```

Expected response:

```json
{
  "status": "alive"
}
```

---

# Start Distributed Master

On the master machine:

```bash
cd distributed-master
python main.py
```

---

# Execution Modes

## Simulation Mode

Used for:

* stress testing
* scalability testing
* concurrency testing
* scheduler/load balancer evaluation

Configure in:

```text
gpu-worker/common/config.py
```

```python
USE_REAL_LLM = False
USE_RAG = False
SIMULATED_PROCESSING_TIME = 0.05
```

Recommended for:

* 1000+ concurrent users
* throughput testing

---

## Real AI Mode

Used for:

* actual AI inference
* RAG demonstrations
* LLM functionality testing

```python
USE_REAL_LLM = True
USE_RAG = True
```

Recommended for:

* functional demonstrations
* AI inference testing

---

# Fault Tolerance

The system supports:

* Worker failure detection
* Request retries
* Worker isolation
* Health checks
* Remote worker monitoring

If a worker fails during execution:

1. The scheduler detects the failure.
2. The worker is marked as dead.
3. The request is retried.
4. Another healthy worker receives the task.

---

# Scaling the System

The architecture supports horizontal scaling through additional GPU worker nodes.

To add more workers:

1. Start `worker_server.py` on another machine.
2. Add the worker IP address to:

```text
distributed-master/common/config.py
```

Example:

```python
WORKER_URLS = [
    "http://192.168.1.25:8001",
    "http://192.168.1.40:8001",
    "http://192.168.1.55:8001"
]
```

---

# Running Tests

## Scheduler Tests

```bash
python distributed-master/tests/testScheduler.py
```

## Worker Tests

```bash
python gpu-worker/tests/testWorker.py
```

## RAG Tests

```bash
python gpu-worker/tests/testRag.py
```

---

# Technologies Used

* Python
* FastAPI
* Uvicorn
* HuggingFace Transformers
* SentenceTransformers
* FAISS
* Asyncio
* ThreadPoolExecutor
* Requests
* Pydantic

---

# Notes

* The system was designed for horizontal scalability.
* Simulation mode should be used for large-scale stress testing.
* Real AI mode should be used for AI functionality demonstrations.
* Real LLM inference is significantly slower than simulation mode due to hardware limitations.

---


