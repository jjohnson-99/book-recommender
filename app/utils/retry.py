from typing import Callable, TypeVar, Tuple, Type
import time

T = TypeVar("T")


def retry(
    fn: Callable[[], T],
    retries: int = 3,
    delay: float = 0.5,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> T:
    last_exception: Exception | None = None

    for attempt in range(retries):
        try:
            return fn()

        except exceptions as e:
            last_exception = e

            if attempt == retries - 1:
                break

            sleep_time = delay * (backoff ** attempt)
            time.sleep(sleep_time)

    if last_exception is not None:
        raise last_exception

    raise RuntimeError("retry() failed without capturing an exception")
