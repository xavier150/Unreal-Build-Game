from . import config
from .build_types import BuildPlatformEnum


def get_built_executable_name(platform: BuildPlatformEnum, is_server: bool) -> str:
    """Executable file name as produced by UBT (named after the game/server target, see config)."""
    base_name = config.server_target_name if is_server else config.game_target_name
    return platform.get_executable_file_name(base_name)


def get_renamed_executable_name(platform: BuildPlatformEnum, is_server: bool) -> str:
    """Executable file name after the post build "rename executable" step (see config)."""
    base_name = config.renamed_server_executable_name if is_server else config.renamed_game_executable_name
    return platform.get_executable_file_name(base_name)
