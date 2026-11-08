import threading
import time
import keyboard
import msvcrt
from typing import List
from rich.live import Live
from rich.console import Console
from rich.text import Text
from rich.highlighter import Highlighter
from .dynamic_console_ui_spinner_type import DisplaySpinnerUi, DisplayDotSpinnerUi
from ..Tasks.GroupedUat.run_builds_class import GroupedBuildTask
from .. import bpl

class NoHighlighter(Highlighter):
    """Highlighter that does nothing - disables automatic highlighting"""
    def highlight(self, text: Text) -> None:
        pass

def draw_builder_task(builder: GroupedBuildTask, colored: bool = False) -> str:
    current_build_title = builder.current_build_title()
    current_progress_text = builder.get_current_progress_text(colored=colored)

    internal_tasks: List[str] = []

    for sequential_build in builder.sequential_builds:
        task_text = f"- {sequential_build.get_task_text(colored=colored)}"
        internal_tasks.append(task_text)
        for sub_task_status in sequential_build.get_sub_task_texts(colored=colored):
            internal_tasks.append(f"\t- {sub_task_status}")

    for zip_task in builder.zip_builder_list:
        zip_task_status = builder.get_zip_builder_task_text(zip_task, colored=colored)
        zip_task_text = f"- {zip_task_status}"
        internal_tasks.append(zip_task_text)

    text = "-" * 60 + "\n"
    text += f"[{current_build_title}] {current_progress_text}" + "\n"
    text += "\n".join(internal_tasks)

    return text

class DisplayControlUi:
    def __init__(self) -> None:
        self.title = "Dynamic Console UI"
        self.escape_pressed: bool = False
        self.builder_list: List[GroupedBuildTask] = []
        self.global_progress: float = 0.0
        self.tick_time: float = 0.1  # Time in seconds between UI updates
        self.console: Console = Console(highlighter=NoHighlighter())
        self.live: Live | None = None
        self.spinner: DisplaySpinnerUi = DisplaySpinnerUi()
        self.dot_spinner: DisplayDotSpinnerUi = DisplayDotSpinnerUi()
        self.start_time: float = time.time()

    def get_elapsed_time(self) -> float:
        return time.time() - self.start_time

    def start(self) -> threading.Thread:
        progress_thread: threading.Thread = threading.Thread(target=self.tick_update, daemon=True)
        progress_thread.start()
        return progress_thread

    def tick_update(self) -> None:
        self.live = Live(console=self.console, refresh_per_second=10)
        self.live.start()
        
        try:
            while True:
                self.check_escape()

                cummulated_progress: float = 0.0
                for builder in self.builder_list:
                    cummulated_progress += builder.current_progress_factor()
                self.global_progress: float = cummulated_progress / len(self.builder_list) if self.builder_list else 0.0

                ui_content = self.build_ui_content()
                self.live.update(ui_content)
                
                self.spinner.update_spinner()
                self.dot_spinner.update_spinner()
                time.sleep(self.tick_time)
                
                # Check if all builders have finished
                all_builders_finished = all(builder.get_build_finished() for builder in self.builder_list)
                if self.global_progress >= 1.0 and all_builders_finished:
                    # Force a final update to display the final "Successfully!" status
                    ui_content = self.build_ui_content()
                    self.live.update(ui_content)
                    break
        finally:
            self.live.stop()
        

    def check_escape(self):
        # If windows:

        if msvcrt:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\x1b':  # 0x1b = ESC
                    self.escape_pressed = True
                    print("Escape pressed! Stopping builds...")
                    for builder in self.builder_list:
                        builder.send_stop_request()
        else:
            if keyboard.is_pressed('escape'):  # type: ignore
                self.escape_pressed = True
                print("Escape pressed! Stopping builds...")
                for builder in self.builder_list:
                    builder.send_stop_request()
        

    def build_ui_content(self) -> str:
        """Builds the UI content with rich colorization"""
        lines: List[str] = []
        lines.append("")
        
        # Ajouter le spinner animé avec la progression
        spinner = self.spinner.get_current_spinner_char()
        lines.append(f"[bold]{self.title}[/bold] {spinner}")
        lines.append(f"Build in Progress... {self.global_progress:.0%} complete")
        time_str = bpl.utils.get_formatted_time(self.get_elapsed_time())
        lines.append(f"Time Elapsed: {time_str}")
        lines.append("")
        
        for builder in self.builder_list:
            # Get text without ANSI codes
            builder_text = draw_builder_task(builder, colored=False)
            
            # Apply colorization with rich markup
            builder_text_colored = self._apply_rich_colors(builder_text)
            lines.append(builder_text_colored)

        if self.escape_pressed:
            lines.append("")
            lines.append("Escape was pressed! Build is stopping...")
        else:
            lines.append("")
            lines.append("Press Escape to stop builds...")
        
        lines.append("")
        return "\n".join(lines)

    def _apply_rich_colors(self, text: str) -> str:
        """Applies rich colors to text based on status"""
        # Replace status texts with their rich markup equivalent
        dot_spinner = self.dot_spinner.get_current_dot_state()
        text = text.replace("In progress...", f"[yellow]In progress{dot_spinner}[/yellow]")
        text = text.replace("Successfully!", "[green]Successfully![/green]")
        text = text.replace("Failed!", "[red]Failed![/red]")
        text = text.replace("Canceled!", "[red]Canceled![/red]")
        return text

    def draw_console_ui(self) -> None:
        """Deprecated - kept for backward compatibility"""
        pass

