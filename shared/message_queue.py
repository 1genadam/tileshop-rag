from typing import Any, Callable
import json
import threading
from queue import Queue

class MessageQueue:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MessageQueue, cls).__new__(cls)
                cls._instance.initialize()
            return cls._instance

    def initialize(self):
        self.queues = {}
        self.subscribers = {}

    def create_queue(self, queue_name: str):
        if queue_name not in self.queues:
            self.queues[queue_name] = Queue()
            self.subscribers[queue_name] = []

    def publish(self, queue_name: str, message: Any):
        if queue_name in self.queues:
            message_str = json.dumps(message) if isinstance(message, (dict, list)) else str(message)
            self.queues[queue_name].put(message_str)
            self._notify_subscribers(queue_name, message_str)

    def subscribe(self, queue_name: str, callback: Callable):
        if queue_name in self.subscribers:
            self.subscribers[queue_name].append(callback)

    def _notify_subscribers(self, queue_name: str, message: str):
        for callback in self.subscribers[queue_name]:
            callback(message)
