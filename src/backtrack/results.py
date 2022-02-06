"""backtrack.results"""
import time
from dataclasses import dataclass
from enum import Enum


class OperationStatus(Enum):
    FAILED = "FAILED"
    INCOMPLETE = "INCOMPLETE"
    COMPLETE = "COMPLETE"


@dataclass
class OperationResult:
    name: str
    status_reason: str = None
    status: Enum = OperationStatus.INCOMPLETE
    exc: Exception = None
    duration: float = 0
    start_time: float = time.perf_counter()

    def __repr__(self) -> str:
        return f"<OperationResult coroutine: {self.name}; status: {self.status}; status_reason: {self.status_reason}; duration: {self.duration:0.2f} seconds>"

    def record(self, status: OperationStatus, status_reason: str, exc: Exception = None) -> None:
        self.status = status
        self.duration = time.perf_counter() - self.start_time
        self.status_reason = status_reason
        self.exc = exc
