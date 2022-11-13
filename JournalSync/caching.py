from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field
import json


class CacheInterface(ABC):
    """Interface for caching"""

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abstractmethod
    def put(self, key: str, data: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str) -> Any:
        raise NotImplementedError


@dataclass
class LocalCache(CacheInterface):
    """Implementation of cache interface to provide a local cache
    in the form of a key pair value saved in a json file"""

    path: Path
    cache: dict = field(init=False)

    def __post_init__(self):
        self.cache = {}
        if Path.is_file(self.path):
            self.load_cache()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dump_cache()

    def load_cache(self):
        with open(self.path, "r") as cache:
            self.cache = json.load(cache)

    def dump_cache(self):
        with open(self.path, "w") as cache:
            json.dump(self.cache, cache)

    def put(self, key: str, data: Any) -> None:
        self.cache[key] = data

    def get(self, key: str) -> Any:
        return self.cache[key]
