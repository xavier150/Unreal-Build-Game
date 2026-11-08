from pathlib import Path
from .. import config
from .. import unreal_engine_path
from . import config_file_make

def check_additional_build_files_notes_exists() -> bool:
    """
    Check if additional build files notes file exists
    """
    config_file_path: Path = unreal_engine_path.get_additional_build_files_path() / config.additional_build_files_notes_name
    return config_file_path.is_file()  

def check_additional_build_files_config_exists() -> bool:
    """
    Check if additional build files configuration file exists
    """
    config_file_path: Path = unreal_engine_path.get_additional_build_files_path() / config.additional_build_files_config_name
    return config_file_path.is_file()

def init_additional_build_files_folder() -> None:
    """
    Initialize the additional build files folder if it does not exist
    """
    additional_build_files_path: Path = unreal_engine_path.get_additional_build_files_path()
    if not additional_build_files_path.exists():
        additional_build_files_path.mkdir(parents=True, exist_ok=True)

    if not check_additional_build_files_notes_exists():
        # Copy additional build files notes file
        note_path = Path(__file__).parent / "Notes.md"
        note_target_path: Path = additional_build_files_path / config.additional_build_files_notes_name
        note_target_path.write_text(note_path.read_text())
        print(f"Copied additional build files notes file to {note_target_path}")

    if not check_additional_build_files_config_exists():
        config_file_make.create_base_config_file()