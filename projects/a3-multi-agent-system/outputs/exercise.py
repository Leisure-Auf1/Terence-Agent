# Exercise for Node 2
# TODO: Implement retry and cache_ttl decorators
from functools import wraps
import time
from typing import Any, Callable, Optional

def retry(max_tries: int = 3, delay: float = 1) -> Callable:
    # TODO: student implements
    pass

def cache_ttl(seconds: float = 30) -> Callable:
    # TODO: student implements
    pass
