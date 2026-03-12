"""AegisNet Worker — processes background AI tasks from Redis queue."""

import os
from redis import Redis
from rq import Worker, Queue, Connection
from config import settings

# Redis connection for the queue
conn = Redis.from_url(settings.redis_url)

if __name__ == "__main__":
    # Start the worker, listening on the 'aegis-tasks' queue
    with Connection(conn):
        worker = Worker(["aegis-tasks"])
        print("AegisNet Worker starting... Listening on 'aegis-tasks'")
        worker.work()
