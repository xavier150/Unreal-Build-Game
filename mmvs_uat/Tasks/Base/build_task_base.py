from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import time
import traceback
from typing import Generator, List, Optional
from ... import bpl


class BuildTaskBase:
    """Common base for the leaf sub-tasks tracked by a grouped task (UAT build, post-build action, zip creation)."""

    def __init__(self):
        self.start_time: float = -1.0
        self.end_time: float = -1.0
        self.print_logs: bool = True
        self.cancel_requested: bool = False
        self.success: bool = False
        self.pipeline_log_path: Optional[Path] = None

    def set_pipeline_log_path(self, path: Path) -> None:
        self.pipeline_log_path = path

    def write_pipeline_log(self, message: str) -> None:
        if self.pipeline_log_path is not None:
            timestamp = datetime.now().isoformat(timespec="milliseconds")
            with self.pipeline_log_path.open("a", encoding="utf-8") as log_file:
                log_file.write(f"[{timestamp}] {message}\n")

    @contextmanager
    def log_step(self, label: str) -> Generator[None, None, None]:
        started = time.perf_counter()
        self.write_pipeline_log(f"START {label}")
        try:
            yield
        except BaseException:
            self.write_pipeline_log(
                f"ERROR {label}\n{traceback.format_exc()}"
            )
            raise
        finally:
            self.write_pipeline_log(
                f"END {label} | duration={time.perf_counter() - started:.3f}s"
            )

    def print_log(self, *values: object) -> None:
        """Prints a message if print_logs is enabled."""
        self.write_pipeline_log(" ".join(str(value) for value in values))
        if self.print_logs:
            print(*values)

    def send_stop_request(self) -> None:
        self.cancel_requested = True

    def get_build_finished(self) -> bool:
        """Check if the task has finished (either success or failure)."""
        return self.start_time >= 0.0 and self.end_time >= 0.0

    def current_progress_factor(self) -> float:
        """Returns the current progress of the task. Subclasses can override for finer-grained progress."""
        if self.start_time < 0.0:
            return 0.0
        elif self.end_time >= 0.0:
            return 1.0
        else:
            return 0.5

    def get_current_progress_text(self, colored: bool = True) -> str:
        if self.start_time < 0.0:
            return "Not started."
        elif self.end_time >= 0.0:
            if self.cancel_requested:
                return bpl.color_set.red("Canceled!") if colored else "Canceled!"
            if self.success:
                text = bpl.color_set.green("Successfully!") if colored else "Successfully!"
                text += f" Done in {bpl.utils.get_formatted_time(self.end_time - self.start_time)}"
                return text
            else:
                return bpl.color_set.red("Failed!") if colored else "Failed!"
        else:
            return bpl.color_set.yellow("In progress...") if colored else "In progress..."


class GroupedBuildTaskBase(BuildTaskBase):
    """Base for a task made of ordered sub-tasks (BuildTaskBase) whose progress/success are aggregated."""

    def set_pipeline_log_path(self, path: Path) -> None:
        super().set_pipeline_log_path(path)
        for task in self.get_sub_tasks():
            task.set_pipeline_log_path(path)

    def get_sub_tasks(self) -> List[BuildTaskBase]:
        """Returns the sub-tasks to aggregate. Subclasses must override this."""
        return []

    def current_progress_factor(self) -> float:
        if self.start_time < 0.0:
            return 0.0
        elif self.end_time >= 0.0:
            return 1.0
        else:
            sub_tasks = self.get_sub_tasks()
            if not sub_tasks:
                return 0.0
            return sum(task.current_progress_factor() for task in sub_tasks) / len(sub_tasks)

    def get_build_finished(self) -> bool:
        if self.start_time < 0.0:
            return False
        elif self.end_time >= 0.0:
            return True
        return all(task.get_build_finished() for task in self.get_sub_tasks())

    def compute_success(self) -> bool:
        """Aggregates the success of all sub-tasks. Call once every sub-task has finished."""
        return all(task.success for task in self.get_sub_tasks())

    def send_stop_request(self) -> None:
        super().send_stop_request()
        for task in self.get_sub_tasks():
            task.send_stop_request()

    def get_current_progress_text(self, colored: bool = True) -> str:
        if self.start_time < 0.0:
            return "Not started."
        elif self.end_time >= 0.0:
            if self.cancel_requested:
                return bpl.color_set.red("Canceled!") if colored else "Canceled!"
            if self.success:
                text = bpl.color_set.green("Successfully!") if colored else "Successfully!"
                text += f" Done in {bpl.utils.get_formatted_time(self.end_time - self.start_time)}"
                return text
            else:
                return bpl.color_set.red("Failed!") if colored else "Failed!"
        else:
            current_progress = self.current_progress_factor()
            text = bpl.color_set.yellow("In progress...") if colored else "In progress..."
            text += f" {current_progress:.0%}"
            return text
