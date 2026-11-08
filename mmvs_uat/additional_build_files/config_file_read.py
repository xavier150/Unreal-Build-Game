from typing import Dict, List, Any
import json
from pathlib import Path
from .. import bpl
from .. import config
from .. import unreal_engine_path

def get_folder_at_key(key: str) -> List[str]:
    """
    Read the additional build files configuration file and get the folders to add at the given key
    """

    config_file_path: Path = unreal_engine_path.get_additional_build_files_path() / config.additional_build_files_config_name
    with config_file_path.open('r', encoding='utf-8') as f:
        data: Dict[str, List[str]] = json.load(f)

    if key in data:
        value: Any = data[key]
        if isinstance(value, list):
            return value # type: ignore
        else:
            text = f"Warning: The value for key '{key}' is not a list!"
            print(bpl.color_set.red(text))
            print(bpl.color_set.red(str(value)))
            return []

    else:
        return []