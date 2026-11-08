import threading
from typing import List
from .dynamic_console_ui_type import DisplayControlUi
from ..Tasks.GroupedUat.run_builds_class import GroupedBuildTask
from .. import project_version_utils

def run_dynamic_console_ui(builder_list: List[GroupedBuildTask]) -> threading.Thread:
    display_control_ui = DisplayControlUi()
    display_control_ui.builder_list = builder_list
    human_readable_version = project_version_utils.get_human_readable_project_version()
    display_control_ui.title = f"Build Project {human_readable_version}"
    return display_control_ui.start()
