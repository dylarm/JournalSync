from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from types import TracebackType
from typing import Any, Dict, Optional, Type

logger = logging.getLogger()

CACHE_DIR: Path = Path("cache.json")


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
        if self.path.is_file() and self.path.stat().st_size > 2:
            logger.debug("Loading cache")
            self.load_cache()
        else:
            logger.debug("No cache found, creating file")
            self.path.touch()

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
            logger.debug("Loading cache from %s", self.path.name)
            self.cache = json.load(cache)

    def dump_cache(self) -> None:
        with open(self.path, "w") as cache:
            logger.debug("Writing cache %s", cache)
            json.dump(self.cache, cache)

    def put(self, key: str, data: Any, timeout: Optional[timedelta] = None) -> None:
        timeout_td = timeout if timeout else self.default_timeout
        expire = datetime.now() + timeout_td
        logger.debug("Caching data with timeout %s seconds", timeout_td.total_seconds())
        self.cache[key] = (expire.isoformat(), data)

    def get(self, key: str) -> Any:
        expire_time = datetime.fromisoformat(self.cache[key][0])
        logger.debug("Checking cache if expired (%s)", expire_time.isoformat())
        if datetime.now() < expire_time:
            logger.info("Obtaining data from cache")
            return self.cache[key][1]
        else:
            logger.info("Cached data expired or not found")
            self.cache.pop(key)
            raise KeyError("Key expired or not found")
