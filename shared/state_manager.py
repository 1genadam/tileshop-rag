import threading
from typing import Any, Dict
import json

class StateManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StateManager, cls).__new__(cls)
                cls._instance.initialize()
            return cls._instance

    def initialize(self):
        self._state: Dict[str, Any] = {}
        self._locks: Dict[str, threading.Lock] = {}

    def set_state(self, key: str, value: Any):
        if key not in self._locks:
            self._locks[key] = threading.Lock()
        
        with self._locks[key]:
            self._state[key] = value

    def get_state(self, key: str) -> Any:
        if key not in self._state:
            return None
        
        with self._locks[key]:
            return self._state[key]

    def update_state(self, key: str, value: Any):
        if key not in self._locks:
            self._locks[key] = threading.Lock()
        
        with self._locks[key]:
            if isinstance(value, dict) and key in self._state:
                if isinstance(self._state[key], dict):
                    self._state[key].update(value)
                else:
                    self._state[key] = value
            else:
                self._state[key] = value

    def delete_state(self, key: str):
        if key in self._state:
            with self._locks[key]:
                del self._state[key]
                del self._locks[key]
