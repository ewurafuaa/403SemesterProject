from dataclasses import dataclass
import time
from typing import Optional


@dataclass
class Task:
    task_id: str
    title: str
    course: str
    due_ts: float
    difficulty: str
    status: str = "pending"
    priority: str = "low"
    last_reminder: Optional[str] = None

    def time_remaining(self) -> float:
        return self.due_ts - time.time()