
# Solution for Node 2
from functools import wraps
import time
from typing import Any, Callable, Dict, Optional, Tuple

def retry(max_tries: int = 3, delay: float = 1) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Optional[Exception] = None
            for attempt in range(1, max_tries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_tries:
                        print(f'[RETRY] 第 {attempt} 次尝试失败，即将重试...')
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator

def cache_ttl(seconds: float = 30) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache: Dict[Tuple[Tuple[Any, ...], Tuple[Tuple[str, Any], ...]], Tuple[Any, float]] = {}
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key: Tuple[Tuple[Any, ...], Tuple[Tuple[str, Any], ...]] = (args, tuple(sorted(kwargs.items())))
            now: float = time.time()
            if key in cache:
                result: Any
                expiry: float
                result, expiry = cache[key]
                if now < expiry:
                    return result
            print('正在计算...')
            result = func(*args, **kwargs)
            cache[key] = (result, now + seconds)
            return result
        return wrapper
    return decorator
