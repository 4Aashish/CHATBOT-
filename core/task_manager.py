from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from queue import Queue
from threading import Lock
from typing import Any, Callable
from uuid import uuid4


class TaskState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    action: Callable[[], Any]
    id: str = field(default_factory=lambda: uuid4().hex[:8])
    state: TaskState = TaskState.PENDING
    result: Any = None
    error: str | None = None


class TaskManager:
    """Small synchronous queue: safe by default and easy to make async later."""
    def __init__(self) -> None:
        self._queue: Queue[Task] = Queue()
        self._tasks: dict[str, Task] = {}
        self._lock = Lock()

    def submit(self, action: Callable[[], Any]) -> Task:
        task = Task(action=action)
        with self._lock:
            self._tasks[task.id] = task
        self._queue.put(task)
        return task

    def run_next(self) -> Task | None:
        if self._queue.empty():
            return None
        task = self._queue.get()
        if task.state == TaskState.CANCELLED:
            return task
        task.state = TaskState.RUNNING
        try:
            task.result = task.action()
            task.state = TaskState.COMPLETED
        except Exception as exc:  # tool failures must not kill the CLI
            task.error = str(exc)
            task.state = TaskState.FAILED
        return task

    def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task or task.state != TaskState.PENDING:
            return False
        task.state = TaskState.CANCELLED
        return True
