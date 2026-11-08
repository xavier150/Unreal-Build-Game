import time
import threading
from typing import Optional, List
from ... import bpl
from ... import project_version_utils
from ..Base.build_task_base import BuildTaskBase, GroupedBuildTaskBase
from ..Build.sequential_build_class import SequentialBuild
from ..Zip.zip_build_class import RawZipBuilder


# Reference to the global semaphore for Unreal builds
# Will be initialized from main.py
unreal_build_semaphore: Optional[threading.Semaphore] = None

def set_unreal_build_semaphore(semaphore: threading.Semaphore) -> None:
    """Sets the global semaphore for Unreal builds"""
    global unreal_build_semaphore
    unreal_build_semaphore = semaphore


class GroupedBuildTask(GroupedBuildTaskBase):
    """
    Groups everything needed to produce one platform/build-mode combination:
    the sequential client/server builds (UAT build + post-build action) and the resulting zips.
    """

    def __init__(self):
        super().__init__()

        self.version_type: str = ""
        self.build_name: str = ""

        self.sequential_builds: List[SequentialBuild] = []
        self.zip_builder_list: List[RawZipBuilder] = []

    def new_sequential_build(self) -> SequentialBuild:
        new_sequential_build = SequentialBuild()
        self.sequential_builds.append(new_sequential_build)
        return new_sequential_build

    def new_zip_builder(self) -> RawZipBuilder:
        new_zip_builder = RawZipBuilder()
        self.zip_builder_list.append(new_zip_builder)
        return new_zip_builder

    def get_sub_tasks(self) -> List[BuildTaskBase]:
        sub_tasks: List[BuildTaskBase] = []
        sub_tasks.extend(self.sequential_builds)
        sub_tasks.extend(self.zip_builder_list)
        return sub_tasks

    def get_zip_builder_task_text(self, zip_builder: RawZipBuilder, colored: bool = False) -> str:
        task_status = zip_builder.get_current_progress_text(colored=colored)
        zip_name = zip_builder.zip_destination_file.name
        return f"ZIP: {zip_name} - {task_status}"

    def current_build_title(self) -> str:

        # Get all builders names
        builder_names: List[str] = []
        for sequential_build in self.sequential_builds:
            platform = sequential_build.uat_builder.get_build_platform()
            build_mode = sequential_build.uat_builder.get_build_mode()
            builder_names.append(f"{platform.get_friendly_name()} - {build_mode.get_friendly_name()}")

        if len(builder_names) > 0:
            # Show only no duplicated names
            unique_builder_names = list(set(builder_names))
            return ", ".join(unique_builder_names)

        zip_names: List[str] = []
        for zip_builder in self.zip_builder_list:
            zip_names.append(f"ZIP Creation - {zip_builder.zip_destination_file.name}")

        if len(zip_names) > 0:
            # Show only no duplicated names
            unique_zip_names = list(set(zip_names))
            return ", ".join(unique_zip_names)

        return "Empty build"

    def current_build_status(self) -> str:
        if self.start_time < 0.0:
            return "Not started"
        elif self.end_time >= 0.0:
            return f"Completed in {bpl.utils.get_formatted_time(self.end_time - self.start_time)}"
        else:
            elapsed_time = self.end_time - self.start_time
            return f"In progress... Elapsed time: {bpl.utils.get_formatted_time(elapsed_time)}"

    def current_build_finished(self) -> bool:
        """Check if the current build has finished."""
        return self.end_time >= 0.0

    def get_project_version(self) -> str:
        return project_version_utils.get_project_version()

    def run_all_builds(self):
        if self.cancel_requested:
            now = time.time()
            self.start_time = now
            self.end_time = now
            return None

        semaphore_acquired = False
        try:
            # Acquire semaphore for Unreal builds
            if unreal_build_semaphore is not None:
                if self.print_logs:
                    print(f"Waiting for Unreal Engine lock...")
                with self.log_step(f"WAIT UNREAL LOCK: {self.current_build_title()}"):
                    unreal_build_semaphore.acquire()
                semaphore_acquired = True
                if self.print_logs:
                    print(f"Unreal Engine lock acquired")

            self.start_time = time.time()
            try:
                for sequential_build in self.sequential_builds:
                    if self.cancel_requested:
                        break
                    build_platform = sequential_build.uat_builder.get_build_platform()
                    build_mode = sequential_build.uat_builder.get_build_mode()
                    with self.log_step(
                        f"BUILD {build_platform.name} {build_mode.name} "
                        f"{sequential_build.get_task_kind_text()}"
                    ):
                        build_success = sequential_build.run(self.print_logs)
                    if not build_success:
                        print(f"Build failed for {build_platform.name} - {build_mode.name}. Exiting...")
                        return

            finally:
                if semaphore_acquired and unreal_build_semaphore is not None:
                    unreal_build_semaphore.release()
                    semaphore_acquired = False
                    if self.print_logs:
                        print(f"Unreal Engine lock released")

            # ZIP is done in parallel, no lock necessary
            if len(self.zip_builder_list) > 0:
                for zip_builder in self.zip_builder_list:
                    with zip_builder.log_step(f"ZIP {zip_builder.zip_destination_file}"):
                        zip_success = zip_builder.create_build_zip()
                        zip_builder.write_pipeline_log(
                            f"ZIP RESULT: success={zip_success} | "
                            f"files={zip_builder.files_processed}/{zip_builder.total_files}"
                        )
                    if not zip_success:
                        print("ZIP creation failed. Exiting...")
                        return

            if self.print_logs:
                print("All builds completed successfully.")

        finally:
            if semaphore_acquired and unreal_build_semaphore is not None:
                unreal_build_semaphore.release()
                if self.print_logs:
                    print(f"Unreal Engine lock released")
            self.success = self.compute_success()
            self.end_time = time.time()
            self.write_pipeline_log(
                f"GROUP RESULT: {self.current_build_title()} | "
                f"success={self.success} | canceled={self.cancel_requested}"
            )
