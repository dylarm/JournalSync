import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from types import TracebackType
from typing import Any, Dict, Optional, Type


class CacheInterface(ABC):
    """Interface for caching"""

    def __enter__(self) -> Optional[CacheInterface]:
        raise NotImplementedError

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
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
    cache: Dict[str, Any] = field(init=False)

    def __post_init__(self) -> None:
        self.cache = {}
        if Path.is_file(self.path):
            self.load_cache()

    def __enter__(self) -> Optional[LocalCache]:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.dump_cache()

    def load_cache(self) -> None:
        with open(self.path, "r") as cache:
            self.cache = json.load(cache)

    def dump_cache(self) -> None:
        with open(self.path, "w") as cache:
            json.dump(self.cache, cache)

    def put(self, key: str, data: Any) -> None:
        self.cache[key] = data

    def get(self, key: str) -> Any:
        return self.cache[key]
