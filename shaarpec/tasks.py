"""Task module."""
from typing import Optional, Any
import time

from pydantic import BaseModel
from tqdm.auto import tqdm
import background

from shaarpec.utils import Debugger


class Task(BaseModel):
    """A running task."""

    service: str
    task_id: str
    submitted_at: str
    status: str
    success: Optional[bool]
    progress: Optional[float]
    result: Optional[Any]
    error: Optional[Any]
    debugger: Optional[Debugger]

    @background.task
    def print(self, update_interval: float = 0.1) -> None:
        """Print the progress of the task."""
        initial = 0 if self.progress is None else int(100 * self.progress)

        with tqdm(initial=initial, total=100) as pbar:
            pbar.set_description(f"Task {self.status}")

            while self.status in ("submitted", "queued", "in_progress"):
                time.sleep(update_interval)
                fraction = 0 if self.progress is None else self.progress
                pbar.update(int(100 * fraction) - pbar.n)
                pbar.set_description(f"Task {self.status}")

            pbar.set_description(
                f"Task completed ({'successfully' if self.success else 'failed'})"
            )

    def wait_for_result(self, poll_interval: float = 0.1) -> Optional[Any]:
        """Return when result becomes available."""
        while self.status in ("submitted", "queued", "in_progress"):
            time.sleep(poll_interval)

        if not self.success:
            raise ValueError(
                f"Task failed with status {self.status} and "
                f"{'error: ' + self.error if self.error else 'no message.'}"
            )

        return self.result
