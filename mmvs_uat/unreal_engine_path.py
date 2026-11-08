from pathlib import Path

from . import config


def get_engine_path() -> Path:
    """Path to UnrealEditor-Cmd.exe, relative to engine_folder_path."""
    return config.engine_folder_path / config.engine_executable_relative_path

def get_uat_path() -> Path:
    """Path to RunUAT.bat, relative to engine_folder_path."""
    return config.engine_folder_path / config.uat_relative_path

def get_build_path() -> Path:
    """Path to Build.bat, relative to engine_folder_path."""
    return config.engine_folder_path / config.build_relative_path

def get_project_directory_path() -> Path:
    """Folder containing the .uproject file."""
    return config.project_path.parent

def get_additional_build_files_path() -> Path:
    """Additional build files folder, relative to the project directory."""
    return get_project_directory_path() / config.additional_build_files_folder_name
