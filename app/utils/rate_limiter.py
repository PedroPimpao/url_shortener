from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = monotonic()
        with self._lock:
            attempts = self._requests[key]
            while attempts and attempts[0] <= now - self.window_seconds:
                attempts.popleft()
            if len(attempts) >= self.limit:
                raise HTTPException(
                    status_code=429,
                    detail="Muitas tentativas. Tente novamente mais tarde",
                )
            attempts.append(now)


password_reset_request_limiter = InMemoryRateLimiter(5, 15 * 60)
password_reset_verify_limiter = InMemoryRateLimiter(10, 15 * 60)
password_reset_complete_limiter = InMemoryRateLimiter(10, 15 * 60)


def client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"
