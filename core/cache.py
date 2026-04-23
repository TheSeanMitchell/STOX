"""
core/cache.py — Disk-backed cache with TTL for fetched data.
"""

import os
import json
import time
import hashlib
import logging
from typing import Any, Optional

log = logging.getLogger("stox.cache")


class Cache:
    """Simple file-based JSON cache with per-entry TTL."""

    def __init__(self, data_dir: str):
        self.cache_dir = os.path.join(data_dir, "_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def _key_path(self, key: str) -> str:
        hashed = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed}.json")

    def get(self, key: str) -> Optional[Any]:
        path = self._key_path(key)
        if not os.path.exists(path):
            return None
        try:
            with open(path) as f:
                entry = json.load(f)
            if entry.get("expires_at", 0) < time.time():
                os.remove(path)
                return None
            return entry["value"]
        except Exception as e:
            log.debug(f"Cache read error for '{key}': {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        path = self._key_path(key)
        entry = {
            "key": key,
            "value": value,
            "created_at": time.time(),
            "expires_at": time.time() + ttl,
        }
        try:
            with open(path, "w") as f:
                json.dump(entry, f, default=str)
        except Exception as e:
            log.debug(f"Cache write error for '{key}': {e}")

    def delete(self, key: str):
        path = self._key_path(key)
        if os.path.exists(path):
            os.remove(path)

    def flush_expired(self):
        """Remove all expired entries. Run occasionally."""
        now = time.time()
        for fname in os.listdir(self.cache_dir):
            fpath = os.path.join(self.cache_dir, fname)
            try:
                with open(fpath) as f:
                    entry = json.load(f)
                if entry.get("expires_at", 0) < now:
                    os.remove(fpath)
            except Exception:
                pass
