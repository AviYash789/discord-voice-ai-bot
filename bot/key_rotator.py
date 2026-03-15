import os
import threading


class KeyRotator:
    def __init__(self):
        self._lock = threading.Lock()
        self._keys = self._load_keys()
        self._index = 0

    def _load_keys(self):
        keys = []
        i = 1
        while True:
            key = os.environ.get(f"GROQ_API_KEY_{i}")
            if not key:
                break
            keys.append(key)
            i += 1
        if not keys:
            raise ValueError("No GROQ_API_KEY_* environment variables found.")
        return keys

    def current(self):
        with self._lock:
            return self._keys[self._index]

    def current_masked(self):
        key = self.current()
        if len(key) <= 8:
            return "***"
        return key[:4] + "****" + key[-4:]

    def current_index(self):
        with self._lock:
            return self._index

    def rotate(self):
        with self._lock:
            self._index = (self._index + 1) % len(self._keys)
            return self._keys[self._index]

    def total(self):
        return len(self._keys)
