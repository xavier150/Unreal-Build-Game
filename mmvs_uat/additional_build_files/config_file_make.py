from typing import Dict, List
import json
from pathlib import Path
from .. import config
from .. import unreal_engine_path
from ..build_types import BuildModeEnum, BuildPlatformEnum
from . import utils

def get_base_config_data() -> Dict[str, List[str]]:
    """
    Create a base json configuration for additional build files with all build variants
    Variants:
    - Server, Client
    - Build Platform
    - Build Config
    """

    all_keys: List[str] = []
    for is_server in [True, False]:
        for target_platform in BuildPlatformEnum.get_all_valid_platforms():
            for build_config in BuildModeEnum.get_all_valid_configs():
                key: str = utils.get_config_key(is_server, target_platform, build_config)
                all_keys.append(key)

    # Key and folder with data to add
    data: Dict[str, List[str]] = {}
    for key in all_keys:
        data[key] = []

    return data

def create_base_config_file() -> Path:
    """
    Create a base configuration file in Json for additional build files with all build variants
    """

    data: Dict[str, List[str]] = get_base_config_data()

    config_file_path: Path = unreal_engine_path.get_additional_build_files_path() / config.additional_build_files_config_name
    with config_file_path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    return config_file_path