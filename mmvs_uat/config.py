from typing import List, Dict, Optional
from pathlib import Path
import zipfile

# Import build config types for presets
from .build_types import BuildModeEnum, BuildPlatformEnum, BuildTargetEnum
from .build_config_type import ControlBuildMethod, LaunchBuildConfigStruct, RawBuildConfigStruct, BuildPlatformEnum, PostBuildFileAction

# ENGINE CONFIGURATION
engine_folder_path: Path = Path('M:/MMVS_EngineFiles_v2')
engine_executable_relative_path: str = "Engine/Binaries/Win64/UnrealEditor-Cmd.exe"
uat_relative_path: str = "Engine/Build/BatchFiles/RunUAT.bat"
build_relative_path: str = "Engine/Build/BatchFiles/Build.bat"

# PROJECT CONFIGURATION
project_path: Path = Path('M:/MMVS_ProjectFiles_v2/UnrealProject/MacroMicroVrService.uproject')
# Project folder inside a packaged build (e.g. <Build>/MacroMicroVrService/Content/Paks). Matches the .uproject name.
project_folder_name: str = project_path.stem

# Target names declared in Source/*.Target.cs. UBT names the built executables after them.
editor_target_name: str = "TagEditor"
game_target_name: str = "TagGame"
server_target_name: str = "TagServer"

# Executable names (without extension) applied by the post build "rename executable" step.
renamed_game_executable_name: str = "MacroMicroVrService"
renamed_server_executable_name: str = "MMVS_Server"

additional_build_files_folder_name: str = "AdditionalBuildFiles"
additional_build_files_config_name: str = "Config.json"
additional_build_files_notes_name: str = "Notes.md"

# OUTPUT CONFIGURATION
output_directory_path: Path = Path('F:/MMVS_GameBuilds')

# Set to True to skip actual builds and zips, useful for testing
fake_build_and_zip: bool = False
fake_build_time_seconds: float = 0.2  # Time to simulate for fake builds
fake_zip_time_seconds: float = 1.0  # Time to simulate for fake zips

# Around 10 GB per zip files
# Maximum 9 builds at the same time
# 90 GB of RAM is required for 9 builds
zip_files_inside_ram: bool = True
zip_compression: int = zipfile.ZIP_DEFLATED  # Default compression method for zip files
zip_compression_level: int = 9  # Maximum compression level for zip files (Default is 6)

# Maximum number of simultaneous Unreal builds
# Recommended: 1 to avoid file conflicts
# You can try 2 if you have enough RAM and CPU
max_concurrent_unreal_builds: int = 1
        

game_platform_folder_names: Dict[str, str] = {
    "Win64": "Windows",
    "Linux": "Linux",
    "LinuxArm64": "LinuxArm64",
}

server_platform_folder_names: Dict[str, str] = {
    "Win64": "WindowsServer",
    "Linux": "LinuxServer",
    "LinuxArm64": "LinuxArm64Server",
}

multiprocess: int = 30

project_name: str = "MMVS"
zip_file_format: str = "{project_name} - {app_version} - {platform}.zip"

mod_folder_suffix: str = "_MODS"
debug_folder_suffix: str = "_DEBUG"
uat_logs_folder_name: str = "UAT_LOGS"

debug_launch_build: bool = False # Only used for debug
debug_launch_build_executable_path: Path = Path(r"F:\MMVS_GameBuilds\DebugGame\Windows\MacroMicroVrService.exe") # Only used for debug



# Build Presets
class BuildPreset_v2:
    """Class for build presets."""
    def __init__(self, preset_id: str, title: str):
        self.preset_id = preset_id
        self.title = title
        self.config = RawBuildConfigStruct()

def simple_build_and_launch_preset(preset_id: str, title: str, platform: BuildPlatformEnum, build_mode: BuildModeEnum, build_client: bool = False, build_server: bool = False) -> BuildPreset_v2:
    if not build_client and not build_server:
        raise ValueError("At least one of build_client or build_server must be True.")

    preset = BuildPreset_v2(preset_id, title)
    preset.config.clear_old_files = True
    preset.config.control_build_methods = ControlBuildMethod.SEQUENTIAL
    build_task = preset.config.tasks.add_task()
    if build_client:
        build_task.builds_config.add_new_build(platform, BuildTargetEnum.CLIENT, build_mode, True)
    if build_server:
        build_task.builds_config.add_new_build(platform, BuildTargetEnum.SERVER, build_mode, True)
    build_task.post_build_config.rename_executable = True
    build_task.post_build_config.set_all_file_actions(PostBuildFileAction.DO_NOTHING)
    if build_client:
        preset.config.launch = LaunchBuildConfigStruct(platform, BuildTargetEnum.CLIENT, build_mode)
    else:
        # Disabled for the moment, need a container to manage that.
        # preset.config.launch = LaunchBuildConfigStruct(platform, BuildTargetEnum.SERVER, build_mode)
        pass
    return preset

def simple_build_and_zip_preset(preset_id: str, title: str, platform: BuildPlatformEnum, build_mode: BuildModeEnum, build_client: bool = False, build_server: bool = False) -> BuildPreset_v2:
    if not build_client and not build_server:
        raise ValueError("At least one of build_client or build_server must be True.")

    preset = BuildPreset_v2(preset_id, title)
    preset.config.clear_old_files = True
    preset.config.control_build_methods = ControlBuildMethod.PARALLEL
    build_task = preset.config.tasks.add_task()
    if build_client:
        build_task.builds_config.add_new_build(platform, BuildTargetEnum.CLIENT, build_mode, True)
    if build_server:
        build_task.builds_config.add_new_build(platform, BuildTargetEnum.SERVER, build_mode, True)
    build_task.post_build_config.rename_executable = True
    build_task.post_build_config.set_all_file_actions(PostBuildFileAction.DO_NOTHING)

    # Zip with client and server builds
    zip_task = preset.config.tasks.add_task()
    zip_task_config = zip_task.zip_config.add_zip(build_mode)
    zip_task_config.use_single_format()
    if build_client:
        zip_task_config.add_build_to_zip(platform, BuildTargetEnum.CLIENT, False)
    if build_server:
        zip_task_config.add_build_to_zip(platform, BuildTargetEnum.SERVER, False)

    return preset

def distribution_build_config(fake_build: bool = False) -> BuildPreset_v2:
    if fake_build:
        id = "distribution_build_fake"
        title = "🚀 Distribution Build (Shipping, All Platforms) [DUMMY]"
    else:
        id = "distribution_build"
        title = "🚀 Distribution Build (Shipping, All Platforms)"

    distribution_build = BuildPreset_v2(id, title)
    distribution_build.config.clear_old_files = True
    distribution_build.config.control_build_methods = ControlBuildMethod.PARALLEL
    for platform in BuildPlatformEnum.get_all_valid_platforms():
        distribution_build_task = distribution_build.config.tasks.add_task()
        distribution_build_task.builds_config.add_new_build(platform, BuildTargetEnum.CLIENT, BuildModeEnum.SHIPPING, True, fake_build)
        distribution_build_task.builds_config.add_new_build(platform, BuildTargetEnum.SERVER, BuildModeEnum.SHIPPING, True, fake_build)
        distribution_build_task.post_build_config.rename_executable = True
        distribution_build_task.post_build_config.set_all_file_actions(PostBuildFileAction.MOVE_OUTSIDE)

        # Zip with client and server builds
        distribution_build_task_zip = distribution_build_task.zip_config.add_zip(BuildModeEnum.SHIPPING)
        distribution_build_task_zip.use_single_format()
        distribution_build_task_zip.add_build_to_zip(platform, BuildTargetEnum.CLIENT, False)
        distribution_build_task_zip.add_build_to_zip(platform, BuildTargetEnum.SERVER, False)

        # Zip with debug files
        distribution_build_task_debug_zip = distribution_build_task.zip_config.add_zip(BuildModeEnum.SHIPPING)
        distribution_build_task_debug_zip.use_single_format()
        distribution_build_task_debug_zip.set_prefix("DEBUG_")
        distribution_build_task_debug_zip.add_debug_files_to_zip(platform, BuildTargetEnum.CLIENT)
        distribution_build_task_debug_zip.add_debug_files_to_zip(platform, BuildTargetEnum.SERVER)

        # Zip with mod files
        distribution_build_task_mod_zip = distribution_build_task.zip_config.add_zip(BuildModeEnum.SHIPPING)
        distribution_build_task_mod_zip.use_single_format()
        distribution_build_task_mod_zip.set_prefix("MODS_")
        distribution_build_task_mod_zip.add_mod_files_to_zip(platform, BuildTargetEnum.CLIENT)
        distribution_build_task_mod_zip.add_mod_files_to_zip(platform, BuildTargetEnum.SERVER)
    distribution_build.config.launch = LaunchBuildConfigStruct(BuildPlatformEnum.WIN64, BuildTargetEnum.CLIENT, BuildModeEnum.SHIPPING)
    return distribution_build

def get_available_presets() -> List[BuildPreset_v2]:

    available_presets: List[BuildPreset_v2] = []

    windows_test_build_shipping = simple_build_and_launch_preset("windows_test_build_shipping", "🧪 Windows Test Build and Launch (Shipping, Win64)", BuildPlatformEnum.WIN64, BuildModeEnum.SHIPPING, True, False)
    windows_test_build_debug = simple_build_and_launch_preset("windows_test_build_debug", "🧪 Windows Test Build and Launch (Debug, Win64)", BuildPlatformEnum.WIN64, BuildModeEnum.DEBUG_GAME, True, False)
    windows_test_build_and_server = simple_build_and_launch_preset("windows_test_build_and_server", "🧪 Windows Test Build and Launch (Debug, Win64 + Server)", BuildPlatformEnum.WIN64, BuildModeEnum.DEBUG_GAME, True, True)
    windows_test_server = simple_build_and_launch_preset("windows_test_server", "🧪 Windows Test Server Build and Launch (Debug, Win64 + Server)", BuildPlatformEnum.WIN64, BuildModeEnum.DEBUG_GAME, False, True)
    available_presets.append(windows_test_build_shipping)
    available_presets.append(windows_test_build_debug)
    available_presets.append(windows_test_build_and_server)
    available_presets.append(windows_test_server)

    linux_test_build_shipping = simple_build_and_launch_preset("linux_test_build_shipping", "🐧 Linux Test Build and Launch (Shipping, Linux)", BuildPlatformEnum.LINUX, BuildModeEnum.SHIPPING, True, False)
    linux_test_build_debug = simple_build_and_launch_preset("linux_test_build_debug", "🐧 Linux Test Build and Launch (Debug, Linux)", BuildPlatformEnum.LINUX, BuildModeEnum.DEBUG_GAME, True, False)
    linux_test_build_and_server = simple_build_and_launch_preset("linux_test_build_and_server", "🐧 Linux Test Build and Launch (Debug, Linux + Server)", BuildPlatformEnum.LINUX, BuildModeEnum.DEBUG_GAME, True, True)
    linux_test_server = simple_build_and_launch_preset("linux_test_server", "🐧 Linux Test Server Build and Launch (Debug, Linux + Server)", BuildPlatformEnum.LINUX, BuildModeEnum.DEBUG_GAME, False, True)
    available_presets.append(linux_test_build_shipping)
    available_presets.append(linux_test_build_debug)
    available_presets.append(linux_test_build_and_server)
    available_presets.append(linux_test_server)

    linux_build_shipping_zip = simple_build_and_zip_preset("linux_build_shipping_zip", "🐧📦 Linux Test Build and Launch (Shipping, Linux)", BuildPlatformEnum.LINUX, BuildModeEnum.SHIPPING, True, False)
    linux_build_debug_zip = simple_build_and_zip_preset("linux_build_debug_zip", "🐧📦 Linux Test Build and Launch (Debug, Linux)", BuildPlatformEnum.LINUX, BuildModeEnum.DEBUG_GAME, True, False)
    available_presets.append(linux_build_shipping_zip)
    available_presets.append(linux_build_debug_zip)

    # Windows Game and Linux Server Build Presets
    windows_test_build_and_server_preset = BuildPreset_v2("windows_game_linux_server", "🧪🐧 Windows Game and Linux Server Build (SHIPPING)")
    windows_test_build_and_server_preset.config.clear_old_files = True
    windows_test_build_and_server_preset.config.control_build_methods = ControlBuildMethod.PARALLEL
    build_task = windows_test_build_and_server_preset.config.tasks.add_task()
    build_task.builds_config.add_new_build(BuildPlatformEnum.WIN64, BuildTargetEnum.CLIENT, BuildModeEnum.SHIPPING, True)
    build_task.builds_config.add_new_build(BuildPlatformEnum.LINUX, BuildTargetEnum.SERVER, BuildModeEnum.SHIPPING, True)
    build_task.post_build_config.rename_executable = True
    build_task.post_build_config.set_all_file_actions(PostBuildFileAction.DO_NOTHING)
    windows_test_build_and_server_preset.config.launch = LaunchBuildConfigStruct(BuildPlatformEnum.WIN64, BuildTargetEnum.CLIENT, BuildModeEnum.SHIPPING)
    windows_test_build_and_server_preset.config.launch = LaunchBuildConfigStruct(BuildPlatformEnum.WIN64, BuildTargetEnum.CLIENT, BuildModeEnum.SHIPPING)
    windows_test_build_and_server_preset_zip = build_task.zip_config.add_zip(BuildModeEnum.SHIPPING)
    windows_test_build_and_server_preset_zip.use_single_format()
    windows_test_build_and_server_preset_zip.add_build_to_zip(BuildPlatformEnum.LINUX, BuildTargetEnum.SERVER, False)
    available_presets.append(windows_test_build_and_server_preset)

    game_tester_shipping_build = BuildPreset_v2("game_tester_shipping_build", "🎮 Game Tester Shipping Build (Shipping)")
    game_tester_shipping_build.config.clear_old_files = True
    game_tester_shipping_build.config.control_build_methods = ControlBuildMethod.PARALLEL
    for platform in BuildPlatformEnum.get_all_valid_platforms():
        game_tester_shipping_build_task = game_tester_shipping_build.config.tasks.add_task()
        game_tester_shipping_build_task.builds_config.add_new_build(platform, BuildTargetEnum.CLIENT, BuildModeEnum.SHIPPING, True)
        game_tester_shipping_build_task.builds_config.add_new_build(platform, BuildTargetEnum.SERVER, BuildModeEnum.SHIPPING, True)
        game_tester_shipping_build_task.post_build_config.rename_executable = True
        game_tester_shipping_build_task.post_build_config.manifest_file = PostBuildFileAction.MOVE_OUTSIDE
        game_tester_shipping_build_task.post_build_config.debug_files = PostBuildFileAction.MOVE_OUTSIDE
        game_tester_shipping_build_task.post_build_config.mod_files = PostBuildFileAction.DO_NOTHING
        game_tester_shipping_build_task_zip = game_tester_shipping_build_task.zip_config.add_zip(BuildModeEnum.SHIPPING)
        game_tester_shipping_build_task_zip.use_single_format()
        game_tester_shipping_build_task_zip.add_build_to_zip(platform, BuildTargetEnum.CLIENT, False)
        game_tester_shipping_build_task_zip.add_build_to_zip(platform, BuildTargetEnum.SERVER, False)
    game_tester_shipping_build.config.launch = LaunchBuildConfigStruct(BuildPlatformEnum.WIN64, BuildTargetEnum.CLIENT, BuildModeEnum.SHIPPING)
    available_presets.append(game_tester_shipping_build)

    game_tester_debug_build = BuildPreset_v2("game_tester_debug_build", "🎮 Game Tester Debug Build (DebugGame)")
    game_tester_debug_build.config.clear_old_files = True
    game_tester_debug_build.config.control_build_methods = ControlBuildMethod.PARALLEL
    for platform in BuildPlatformEnum.get_all_valid_platforms():
        game_tester_debug_build_task = game_tester_debug_build.config.tasks.add_task()
        game_tester_debug_build_task.builds_config.add_new_build(platform, BuildTargetEnum.CLIENT, BuildModeEnum.DEBUG_GAME, True)
        game_tester_debug_build_task.builds_config.add_new_build(platform, BuildTargetEnum.SERVER, BuildModeEnum.DEBUG_GAME, True)
        game_tester_debug_build_task.post_build_config.rename_executable = True
        game_tester_debug_build_task.post_build_config.manifest_file = PostBuildFileAction.MOVE_OUTSIDE
        game_tester_debug_build_task.post_build_config.debug_files = PostBuildFileAction.MOVE_OUTSIDE
        game_tester_debug_build_task.post_build_config.mod_files = PostBuildFileAction.DO_NOTHING
        game_tester_debug_build_task_zip = game_tester_debug_build_task.zip_config.add_zip(BuildModeEnum.DEBUG_GAME)
        game_tester_debug_build_task_zip.use_single_format()
        game_tester_debug_build_task_zip.add_build_to_zip(platform, BuildTargetEnum.CLIENT, False)
        game_tester_debug_build_task_zip.add_build_to_zip(platform, BuildTargetEnum.SERVER, False)
    game_tester_debug_build.config.launch = LaunchBuildConfigStruct(BuildPlatformEnum.WIN64, BuildTargetEnum.CLIENT, BuildModeEnum.DEBUG_GAME)
    available_presets.append(game_tester_debug_build)

    full_build = BuildPreset_v2("full_build", "🔨 Full Build (All configs, All platforms)")
    full_build.config.clear_old_files = True
    full_build.config.control_build_methods = ControlBuildMethod.PARALLEL
    for platform in BuildPlatformEnum.get_all_valid_platforms():
        for build_mode in BuildModeEnum.get_all_valid_configs():
            full_build_task = full_build.config.tasks.add_task()
            full_build_task.builds_config.add_new_build(platform, BuildTargetEnum.CLIENT, build_mode, True)
            full_build_task.builds_config.add_new_build(platform, BuildTargetEnum.SERVER, build_mode, True)
            full_build_task.post_build_config.rename_executable = True
            full_build_task.post_build_config.set_all_file_actions(PostBuildFileAction.MOVE_OUTSIDE)
            full_build_task_zip = full_build_task.zip_config.add_zip(build_mode)
            full_build_task_zip.use_single_format()
            full_build_task_zip.add_build_to_zip(platform, BuildTargetEnum.CLIENT, False)
            full_build_task_zip.add_build_to_zip(platform, BuildTargetEnum.SERVER, False)
    full_build.config.launch = LaunchBuildConfigStruct(BuildPlatformEnum.WIN64, BuildTargetEnum.CLIENT, BuildModeEnum.DEBUG_GAME)
    available_presets.append(full_build)

    full_build_no_package = BuildPreset_v2("full_build_no_package", "🔨 Full Build No Package (All configs, All platforms)")
    full_build_no_package.config.clear_old_files = True
    full_build_no_package.config.control_build_methods = ControlBuildMethod.PARALLEL
    for platform in BuildPlatformEnum.get_all_valid_platforms():
        for build_mode in BuildModeEnum.get_all_valid_configs():
            full_build_no_package_task = full_build_no_package.config.tasks.add_task()
            full_build_no_package_task.builds_config.add_new_build(platform, BuildTargetEnum.CLIENT, build_mode, True)
            full_build_no_package_task.builds_config.add_new_build(platform, BuildTargetEnum.SERVER, build_mode, True)
    full_build_no_package.config.launch = None
    available_presets.append(full_build_no_package)

    rezip_all = BuildPreset_v2("rezip_all", "📦 Rezip All (All configs, All platforms)")
    rezip_all.config.clear_old_files = False
    rezip_all.config.control_build_methods = ControlBuildMethod.PARALLEL
    for platform in BuildPlatformEnum.get_all_valid_platforms():
        for build_mode in BuildModeEnum.get_all_valid_configs():
            rezip_all_task = rezip_all.config.tasks.add_task()
            rezip_all_task_zip = rezip_all_task.zip_config.add_zip(build_mode)
            rezip_all_task_zip.use_single_format()
            rezip_all_task_zip.add_build_to_zip(platform, BuildTargetEnum.CLIENT, False)
            rezip_all_task_zip.add_build_to_zip(platform, BuildTargetEnum.SERVER, False)
    available_presets.append(rezip_all)


    distribution_build_preset = distribution_build_config()
    available_presets.append(distribution_build_preset)
    dummy_distribution_build_preset = distribution_build_config(fake_build=True)
    available_presets.append(dummy_distribution_build_preset)
    return available_presets

# List of available presets v2
available_config_presets_v2: List[BuildPreset_v2] = get_available_presets()

def get_preset_config(preset_id: str) -> Optional[RawBuildConfigStruct]:
    """
    Get the build configuration for a specific preset.
    
    Args:
        preset_id: The ID of the preset
        
    Returns:
        RawBuildConfigStruct with the preset configuration, or None if preset not found
    """
    for preset in available_config_presets_v2:
        if preset.preset_id == preset_id:
            return preset.config
    return None