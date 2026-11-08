from ..build_types import BuildModeEnum, BuildPlatformEnum

def get_config_key(is_server: bool, target_platform: BuildPlatformEnum, build_config: BuildModeEnum) -> str:
    get_folder_search: str = ""
    get_folder_search += "Server_" if is_server else "Client_"
    get_folder_search += target_platform.value + "_"
    get_folder_search += build_config.value
    return get_folder_search