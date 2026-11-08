import shutil
import zipfile
from pathlib import Path
from . import bpl

############## Manifest files actions ##############

def move_manifest_files_outside(path: Path, suffix: str = "_MANIFEST", print_logs: bool = True) -> None:
    """
    This function moves manifest files outside the build folder
    """
    # Add folder at the end of path
    destination_folder: Path = path.with_name(path.name + suffix)
    for file_path in path.iterdir():
        if file_path.is_file() and file_path.name.startswith("Manifest_"):
            relative_path = file_path.relative_to(path)
            new_file_path = destination_folder / relative_path
            new_file_dir = new_file_path.parent
            new_file_dir.mkdir(parents=True, exist_ok=True)
            try:
                file_path.rename(new_file_path)
                if print_logs:
                    print(f"File moved : {file_path} to {new_file_path}")
            except Exception as e:
                print(bpl.color_set.red(f"Failed to move {file_path} to {new_file_path}: {e}"))

def copy_manifest_files_outside(path: Path, suffix: str = "_MANIFEST", print_logs: bool = True) -> None:
    """
    This function copies manifest files outside the build folder
    """
    # Add folder at the end of path
    destination_folder: Path = path.with_name(path.name + suffix)
    for file_path in path.iterdir():
        if file_path.is_file() and file_path.name.startswith("Manifest_"):
            relative_path = file_path.relative_to(path)
            new_file_path = destination_folder / relative_path
            new_file_dir = new_file_path.parent
            new_file_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(file_path, new_file_path)
                if print_logs:
                    print(f"File copied : {file_path} to {new_file_path}")
            except Exception as e:
                print(bpl.color_set.red(f"Failed to copy {file_path} to {new_file_path}: {e}"))

def remove_manifest_files(path: Path, suffix: str = "_MANIFEST", print_logs: bool = True) -> None:
    """
    This function removes manifest files from the build folder
    """
    for file_path in path.iterdir():
        if file_path.is_file() and file_path.name.startswith("Manifest_"):
            try:
                file_path.unlink()
                if print_logs:
                    print(f"File removed : {file_path}")
            except Exception as e:
                print(bpl.color_set.red(f"Failed to remove {file_path}: {e}"))
    
############### Debug files actions ##############

def move_debug_files_outside(path: Path, suffix: str = "_DEBUG", print_logs: bool = True) -> None:
    """
    This function moves debug files (.pdb, .debug and .sym) outside the build folder
    """
    file_search_patterns = ['*.pdb', '*.debug', '*.sym']

    # Add folder at the end of path
    destination_folder: Path = path.with_name(path.name + suffix)
    for pattern in file_search_patterns:
        for file_path in path.rglob(pattern):
            if file_path.is_file():
                relative_path = file_path.relative_to(path)
                new_file_path = destination_folder / relative_path
                new_file_dir = new_file_path.parent
                new_file_dir.mkdir(parents=True, exist_ok=True)
                try:
                    file_path.rename(new_file_path)
                    if print_logs:
                        print(f"File moved : {file_path} to {new_file_path}")
                except Exception as e:
                    print(bpl.color_set.red(f"Failed to move {file_path} to {new_file_path}: {e}"))

def copy_debug_files_outside(path: Path, suffix: str = "_DEBUG", print_logs: bool = True) -> None:
    """
    This function copies debug files (.pdb, .debug and .sym) outside the build folder
    """
    file_search_patterns = ['*.pdb', '*.debug', '*.sym']

    # Add folder at the end of path
    destination_folder: Path = path.with_name(path.name + suffix)
    for pattern in file_search_patterns:
        for file_path in path.rglob(pattern):
            if file_path.is_file():
                relative_path = file_path.relative_to(path)
                new_file_path = destination_folder / relative_path
                new_file_dir = new_file_path.parent
                new_file_dir.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(file_path, new_file_path)
                    if print_logs:
                        print(f"File copied : {file_path} to {new_file_path}")
                except Exception as e:
                    print(bpl.color_set.red(f"Failed to copy {file_path} to {new_file_path}: {e}"))

def remove_debug_files(path: Path, suffix: str = "_DEBUG", print_logs: bool = True) -> None:
    """
    This function removes debug files (.pdb, .debug and .sym) from the build folder
    """
    file_search_patterns = ['*.pdb', '*.debug', '*.sym']

    for pattern in file_search_patterns:
        for file_path in path.rglob(pattern):
            if file_path.is_file():
                try:
                    file_path.unlink()
                    if print_logs:
                        print(f"File removed : {file_path}")
                except Exception as e:
                    print(bpl.color_set.red(f"Failed to remove {file_path}: {e}"))

################ Mod files actions ##############

def move_mods_files_outside(path: Path, suffix: str = "_MODS", print_logs: bool = True) -> None:
    r"""
    This function moves mod files (pakchunk101-999) outside the build folder
    Automatically detects all mod files with pakchunk pattern from 101 to 999
    Example: 
    Path = "F:\MMVS_GameBuilds\DebugGame\Windows"
    "pakchunk101-Windows.pak" is a mod file
    "pakchunk101-Windows.pak" is found in "F:\MMVS_GameBuilds\DebugGame\Windows\MacroMicroVrService\Content\Paks"
    The file is moved to path + "_MODS" and keeps the same subfolder structure
    So "F:\MMVS_GameBuilds\DebugGame\Windows_MODS\MacroMicroVrService\Content\Paks"
    """
    import re
    
    # Pattern to detect mod files pakchunk101-999
    mod_pattern = re.compile(r'^pakchunk([1-9]\d{2})-.*\.(pak|sig)$')

    # Add folder at the end of path
    destination_folder: Path = path.with_name(path.name + suffix)
    for file_path in path.rglob('*'):
        if file_path.is_file():
            # Check if the file matches the mod pattern
            match = mod_pattern.match(file_path.name)
            if match:
                chunk_number = int(match.group(1))
                # Check that it is within the range 101-999
                if 101 <= chunk_number <= 999:
                    relative_path = file_path.relative_to(path)
                    new_file_path = destination_folder / relative_path
                    new_file_dir = new_file_path.parent
                    new_file_dir.mkdir(parents=True, exist_ok=True)
                    try:
                        file_path.rename(new_file_path)
                        if print_logs:
                            print(f"Mod file moved : {file_path} to {new_file_path}")
                    except Exception as e:
                        print(bpl.color_set.red(f"Failed to move {file_path} to {new_file_path}: {e}"))
            elif file_path.name.startswith("pakchunk") and print_logs:  # Debug for other pakchunk files
                print(f"Found pakchunk file but not a mod (101-999): {file_path.name}")

def copy_mods_files_outside(path: Path, suffix: str = "_MODS", print_logs: bool = True) -> None:
    r"""
    This function copies mod files (pakchunk101-999) outside the build folder
    Automatically detects all mod files with pakchunk pattern from 101 to 999
    Example: 
    Path = "F:\MMVS_GameBuilds\DebugGame\Windows"
    "pakchunk101-Windows.pak" is a mod file
    "pakchunk101-Windows.pak" is found in "F:\MMVS_GameBuilds\DebugGame\Windows\MacroMicroVrService\Content\Paks"
    The file is copied to path + "_MODS" and keeps the same subfolder structure
    So "F:\MMVS_GameBuilds\DebugGame\Windows_MODS\MacroMicroVrService\Content\Paks"
    """
    import re
    
    # Pattern to detect mod files pakchunk101-999
    mod_pattern = re.compile(r'^pakchunk([1-9]\d{2})-.*\.(pak|sig)$')

    # Add folder at the end of path
    destination_folder: Path = path.with_name(path.name + suffix)
    for file_path in path.rglob('*'):
        if file_path.is_file():
            # Check if the file matches the mod pattern
            match = mod_pattern.match(file_path.name)
            if match:
                chunk_number = int(match.group(1))
                # Check that it is within the range 101-999
                if 101 <= chunk_number <= 999:
                    relative_path = file_path.relative_to(path)
                    new_file_path = destination_folder / relative_path
                    new_file_dir = new_file_path.parent
                    new_file_dir.mkdir(parents=True, exist_ok=True)
                    try:
                        shutil.copy2(file_path, new_file_path)
                        if print_logs:
                            print(f"Mod file copied : {file_path} to {new_file_path}")
                    except Exception as e:
                        print(bpl.color_set.red(f"Failed to copy {file_path} to {new_file_path}: {e}"))
            elif file_path.name.startswith("pakchunk") and print_logs:  # Debug for other pakchunk files
                print(f"Found pakchunk file but not a mod (101-999): {file_path.name}")

def remove_mods_files(path: Path, suffix: str = "_MODS", print_logs: bool = True) -> None:
    r"""
    This function removes mod files (pakchunk101-999) from the build folder
    Automatically detects all mod files with pakchunk pattern from 101 to 999
    """
    import re
    
    # Pattern to detect mod files pakchunk101-999
    mod_pattern = re.compile(r'^pakchunk([1-9]\d{2})-.*\.(pak|sig)$')

    for file_path in path.rglob('*'):
        if file_path.is_file():
            # Check if the file matches the mod pattern
            match = mod_pattern.match(file_path.name)
            if match:
                chunk_number = int(match.group(1))
                # Check that it is within the range 101-999
                if 101 <= chunk_number <= 999:
                    try:
                        file_path.unlink()
                        if print_logs:
                            print(f"Mod file removed : {file_path}")
                    except Exception as e:
                        print(bpl.color_set.red(f"Failed to remove {file_path}: {e}"))
            elif file_path.name.startswith("pakchunk") and print_logs:  # Debug for other pakchunk files
                print(f"Found pakchunk file but not a mod (101-999): {file_path.name}")

################ Zip files actions ##############

def create_zip_archive(source_path: Path, destination_filepath: Path) -> None:
    """Creates a ZIP archive from the source path to the destination filepath."""
    with zipfile.ZipFile(destination_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_path.rglob('*'):
            if file_path.is_file():
                zipf.write(file_path, file_path.relative_to(source_path))