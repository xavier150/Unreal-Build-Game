import shutil
import time
from pathlib import Path
from . import bpl
from . import config
from .Tasks.Build.raw_uat_builder_class import RawUATBuilder
from . import unreal_engine_path

# List of folder and file paths to delete (relative to the project directory)

temp_files = [
    f"{config.project_path.stem}.sln",
    ".vsconfig",
]

temp_folders = [
    "Saved",
    "Intermediate",
    ".vs",
    "Binaries",
    "DerivedDataCache",
]

def remove_temp_folders() -> None:
    project_folder: Path = unreal_engine_path.get_project_directory_path()

    for file_path in temp_files:
        file_to_remove = project_folder / file_path
        remove_file(file_to_remove)


    for folder_path in temp_folders:
        folder_to_remove = project_folder / folder_path
        remove_folder(folder_to_remove)

def remove_file(path: Path) -> None:
    try:
        if path.is_file():
            path.unlink()
            print(f"File deleted: {path}")
        else:
            print(f"Path does not exist: {path}")
    except Exception as e:
        print(f"Error deleting {path}: {e}")


def remove_folder(path: Path) -> None:
    try:
        if path.is_dir():
            shutil.rmtree(path)
            print(f"Folder deleted: {path}")
        else:
            print(f"Path does not exist: {path}")
    except Exception as e:
        print(f"Error deleting {path}: {e}")

#remove_temp_folders()

def ask_start_brut_force_input() -> bool:
    print("Rebuild project? Press Enter to continue.")
    response: str = input()
    return response == ''

def countdown(t: float, update_interval: float = 0.1) -> None:
    # Convert total time to seconds
    total_seconds: int = int(t * 10)  # Multiply by 10 to handle tenths of seconds
    while total_seconds > 0:
        # Convert total_seconds back to normal seconds for display
        mins, secs = divmod(total_seconds / 10, 60)
        secs, tenths = divmod(secs, 1)  # Separate seconds and tenths of seconds
        time_format = '{:02d}:{:02d}.{:1d}'.format(int(mins), int(secs), int(tenths * 10))
        print(time_format, end='\r')
        time.sleep(update_interval)
        total_seconds -= 1  # Reduce in 'ticks' of tenth of second
    print("Time elapsed!")


def start_user_ui() -> None:
    # Clear console; works differently depending on OS
    bpl.console_utils.clear_console()

    ask_config: bool = False
    if ask_config:
        brut_force_confirm: bool = ask_start_brut_force_input()  # Ask for user confirmation
        if brut_force_confirm is False:
            print("Procedure cancelled...")
            return
    
    run_build()



def run_build() -> None:
    print("Start Remove Temp Folders.")
    remove_temp_folders()

    countdown(1, 0.1)
    print("Start build")
    timer = bpl.utils.CounterTimer()
    uat_builder = RawUATBuilder()
    uat_builder.target_platform = "Win64"
    uat_builder.platform = "Win64"
    uat_builder.server_platform = "Win64"
    uat_builder.multiprocess = 1
    uat_builder.client_config = "Shipping"
    uat_builder.server_config = "Shipping"
    uat_builder.build_batch = unreal_engine_path.get_build_path()
    #uat_builder.start_build()


    command = (
        f'{uat_builder.build_batch} '
        f'-Target="{config.editor_target_name} Win64 Development -Project=\\"{config.project_path}\\"" '
        f'-Target="ShaderCompileWorker Win64 Development -Quiet" -WaitMutex -FromMsBuild'
    )
    uat_builder.start_build_with_command(command)
    print("Finished in", timer.get_str_time() )
