import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
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
    default_timeout: timedelta = timedelta(hours=1)

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

    def put(self, key: str, data: Any, timeout: Optional[timedelta] = None) -> None:
        timeout_td = timeout if timeout else self.default_timeout
        expire = datetime.now() + timeout_td
        self.cache[key] = (expire.isoformat(), data)

    def get(self, key: str) -> Any:
        expire_time = datetime.fromisoformat(self.cache[key][0])
        if datetime.now() < expire_time:
            return self.cache[key][1]
        else:
            self.cache.pop(key)
            raise KeyError("Key expired or not found")
