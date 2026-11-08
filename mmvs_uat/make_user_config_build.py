from typing import List
from enum import Enum
from .user_input import PlayerInput
from .build_config_type import ControlBuildMethod, RawBuildConfigStruct, LaunchBuildConfigStruct, PostBuildFileAction
from .build_types import BuildPlatformEnum, BuildModeEnum, BuildTargetEnum
from . import bpl



def get_control_build_methods() -> ControlBuildMethod:
    player_input = PlayerInput()

    # Ask user to choose the builds to perform
    player_input.set_title("Console build method :")
    player_input.set_input_description("Enter the number corresponding to the console build method: ")
    player_input.add_number_option(ControlBuildMethod.SEQUENTIAL, 'Stable (Sequential with all logs)')
    player_input.add_number_option(ControlBuildMethod.PARALLEL, 'Parallel (Parallel builds and progress UI)')

    result = player_input.ask_player_input()
    if isinstance(result, ControlBuildMethod):
        return result
    else:
        raise ValueError("Invalid build configuration selected. Please choose a valid option.")  

class UserBuildModeEnum(Enum):
    ALL = "All"
    DEBUG_GAME = "DebugGame"
    DEVELOPMENT = "Development"
    SHIPPING = "Shipping"

    def get_friendly_name(self) -> str:
        if self.value == UserBuildModeEnum.ALL.value:
            return "All"
        elif self.value == UserBuildModeEnum.DEBUG_GAME.value:
            return "Debug Game"
        elif self.value == UserBuildModeEnum.DEVELOPMENT.value:
            return "Development"
        elif self.value == UserBuildModeEnum.SHIPPING.value:
            return "Shipping"
        else:
            raise ValueError("Invalid build configuration selected. Please choose a valid option.")
    
    def get_build_modes(self) -> List[BuildModeEnum]: 
        if self.value == UserBuildModeEnum.ALL.value:
            return BuildModeEnum.get_all_valid_configs()
        elif self.value == UserBuildModeEnum.DEBUG_GAME.value:
            return [BuildModeEnum.DEBUG_GAME]
        elif self.value == UserBuildModeEnum.DEVELOPMENT.value:
            return [BuildModeEnum.DEVELOPMENT]
        elif self.value == UserBuildModeEnum.SHIPPING.value:
            return [BuildModeEnum.SHIPPING]
        else:
            raise ValueError("Invalid build configuration selected. Please choose a valid option.")



def get_build_mode() -> UserBuildModeEnum:
    player_input = PlayerInput()

    # Ask user to choose build configuration
    player_input.set_title("Choose build configuration:")
    player_input.set_input_description("Enter the number corresponding to the build configuration: ")
    for config in UserBuildModeEnum:
        player_input.add_number_option(config, config.get_friendly_name())
    
    result = player_input.ask_player_input()
    if isinstance(result, UserBuildModeEnum):
        return result
    else:
        raise ValueError("Invalid build configuration selected. Please choose a valid option.")

class UserBuildPlatformEnum(Enum):
    ALL = "All"
    WIN64 = "Win64"
    LINUX = "Linux"
    LINUX_ARM64 = "LinuxArm64"

    def get_friendly_name(self) -> str:
        if self.value == UserBuildPlatformEnum.ALL.value:
            return "All"
        elif self.value == UserBuildPlatformEnum.WIN64.value:
            return "Win64"
        elif self.value == UserBuildPlatformEnum.LINUX.value:
            return "Linux"
        elif self.value == UserBuildPlatformEnum.LINUX_ARM64.value:
            return "Linux Arm64"
        else:
            raise ValueError("Invalid build platform selected. Please choose a valid option.")
        
    def get_platforms(self) -> List[BuildPlatformEnum]:
        if self.value == UserBuildPlatformEnum.ALL.value:
            return BuildPlatformEnum.get_all_valid_platforms()
        elif self.value == UserBuildPlatformEnum.WIN64.value:
            return [BuildPlatformEnum.WIN64]
        elif self.value == UserBuildPlatformEnum.LINUX.value:
            return [BuildPlatformEnum.LINUX]
        elif self.value == UserBuildPlatformEnum.LINUX_ARM64.value:
            return [BuildPlatformEnum.LINUX_ARM64]
        else:
            raise ValueError("Invalid build platform selected. Please choose a valid option.")

def get_build_platforms() -> UserBuildPlatformEnum:
    player_input = PlayerInput()

    # Ask user to choose which builds to perform
    player_input.set_title("Choose builds to perform:")
    player_input.set_input_description("Enter the number corresponding to the build configuration: ")
    for platform in UserBuildPlatformEnum:
        player_input.add_number_option(platform, platform.get_friendly_name())

    result = player_input.ask_player_input()
    if isinstance(result, UserBuildPlatformEnum):
        return result
    else:
        raise ValueError("Invalid build configuration selected. Please choose a valid option.")

class UserBuildTargets(Enum):
    CLIENT = "Client"
    SERVER = "Server"
    CLIENT_AND_SERVER = "ClientAndServer"
    NONE = "None"

    def get_friendly_name(self) -> str:
        if self.value == UserBuildTargets.CLIENT.value:
            return "Client Build Only"
        elif self.value == UserBuildTargets.SERVER.value:
            return "Server Build Only"
        elif self.value == UserBuildTargets.CLIENT_AND_SERVER.value:
            return "Client and Server Builds"
        elif self.value == UserBuildTargets.NONE.value:
            return "No Builds"
        else:
            raise ValueError("Invalid build configuration selected. Please choose a valid option.")
        
    def get_build_targets(self) -> List[BuildTargetEnum]:
        if self.value == UserBuildTargets.CLIENT.value:
            return [BuildTargetEnum.CLIENT]
        elif self.value == UserBuildTargets.SERVER.value:
            return [BuildTargetEnum.SERVER]
        elif self.value == UserBuildTargets.CLIENT_AND_SERVER.value:
            return [BuildTargetEnum.CLIENT, BuildTargetEnum.SERVER]
        elif self.value == UserBuildTargets.NONE.value:
            return []
        else:
            raise ValueError("Invalid build configuration selected. Please choose a valid option.")

def get_build_targets() -> UserBuildTargets:
    player_input = PlayerInput()

    # Ask user if they want to create a server build
    player_input.set_title("Target builds:")
    player_input.set_input_description("Enter the corresponding number: ")
    for target in UserBuildTargets:
        player_input.add_number_option(target, target.get_friendly_name())

    result = player_input.ask_player_input()
    if isinstance(result, UserBuildTargets):
        return result
    else:
        raise ValueError("Invalid build configuration selected. Please choose a valid option.")

def get_should_package() -> bool:
    player_input = PlayerInput()

    # Ask user for the package build method
    player_input.set_title("Package build method")
    player_input.set_input_description("Enter the corresponding number: ")
    player_input.add_number_option(False, 'Do Not Package (Build Only)')
    player_input.add_number_option(True, 'Package')

    result = player_input.ask_player_input()
    if isinstance(result, bool):
        return result
    else:
        raise ValueError("Invalid build configuration selected. Please choose a valid option.")
    
class UserZipBuildMethod(Enum):
    DO_NOT_ZIP = "DoNotZip"
    ZIP = "SingleZip" # Client and server in a single zip
    ZIP_WITH_MODS = "SingleZipWithMods"
    ZIP_WITH_EXTRACTED_FILES = "SingleZipWithExtractedFiles"
    SEPARATE_ZIPS = "SeparateZips" # Client and server in separate zips
    SEPARATE_ZIPS_WITH_MODS = "SeparateZipsWithMods"
    SEPARATE_ZIPS_WITH_EXTRACTED_FILES = "SeparateZipsWithExtractedFiles"

    def get_friendly_name(self) -> str:
        if self.value == UserZipBuildMethod.DO_NOT_ZIP.value:
            return "Do Not Zip"
        elif self.value == UserZipBuildMethod.ZIP.value:
            return "Zip (Client and Server in a single zip)"
        elif self.value == UserZipBuildMethod.ZIP_WITH_MODS.value:
            return "Zip with Mods (Client and Server in a single zip, including mod files)"
        elif self.value == UserZipBuildMethod.ZIP_WITH_EXTRACTED_FILES.value:
            return "Zip with Extracted Files (Client and Server in a single zip, with debug and mod files extracted in separate folders)"
        elif self.value == UserZipBuildMethod.SEPARATE_ZIPS.value:
            return "Separate Zips (Client and Server in separate zips)"
        elif self.value == UserZipBuildMethod.SEPARATE_ZIPS_WITH_MODS.value:
            return "Separate Zips with Mods (Client and Server in separate zips, including mod files)"
        elif self.value == UserZipBuildMethod.SEPARATE_ZIPS_WITH_EXTRACTED_FILES.value:
            return "Separate Zips with Extracted Files (Client and Server in separate zips, with debug and mod files extracted in separate folders)"
        else:
            raise ValueError("Invalid zip build method selected. Please choose a valid option.")
        
    def sperate_zips(self) -> bool:
        if self.value in [UserZipBuildMethod.SEPARATE_ZIPS.value, UserZipBuildMethod.SEPARATE_ZIPS_WITH_MODS.value, UserZipBuildMethod.SEPARATE_ZIPS_WITH_EXTRACTED_FILES.value]:
            return True
        else:
            return False
        
    def include_mods(self) -> bool:
        if self.value in [UserZipBuildMethod.ZIP_WITH_MODS.value, UserZipBuildMethod.SEPARATE_ZIPS_WITH_MODS.value]:
            return True
        else:
            return False
        
    def include_extracted_files(self) -> bool:
        if self.value in [UserZipBuildMethod.ZIP_WITH_EXTRACTED_FILES.value, UserZipBuildMethod.SEPARATE_ZIPS_WITH_EXTRACTED_FILES.value]:
            return True
        else:
            return False

def get_zip_method() -> UserZipBuildMethod:
    player_input = PlayerInput()

    # Ask user for the zip build method
    player_input.set_title("Zip build method")
    player_input.set_input_description("Enter the corresponding number: ")
    for method in UserZipBuildMethod:
        player_input.add_number_option(method, method.get_friendly_name())

    result = player_input.ask_player_input()
    if isinstance(result, UserZipBuildMethod):
        return result
    else:
        raise ValueError("Invalid build configuration selected. Please choose a valid option.")

def get_clear_old_files() -> bool:
    player_input = PlayerInput()

    # Ask user if they want to delete files from previous builds
    player_input.set_title("Delete files in the folder?")
    player_input.set_input_description("Enter the corresponding number: ")
    player_input.add_yes_no_options()

    result = player_input.ask_player_input()
    if isinstance(result, bool):
        return result
    else:
        raise ValueError("Invalid build configuration selected. Please choose a valid option.")



def get_launch() -> bool:
    player_input = PlayerInput()

    # Ask user if they want to launch the game after the build is done
    player_input.set_title("Launch game after build is done?")
    player_input.set_input_description("Enter the corresponding number: ")
    player_input.add_yes_no_options()
    
    result = player_input.ask_player_input()
    if isinstance(result, bool):
        return result
    else:
        raise ValueError("Invalid build configuration selected. Please choose a valid option.")


def make_user_config_build() -> RawBuildConfigStruct:
    
    control_build_methods: ControlBuildMethod = get_control_build_methods()
    bpl.console_utils.clear_console()

    build_modes = get_build_mode()
    bpl.console_utils.clear_console()

    build_platforms = get_build_platforms()
    bpl.console_utils.clear_console()

    build_targets = get_build_targets()
    bpl.console_utils.clear_console()

    should_package = get_should_package()
    bpl.console_utils.clear_console()

    if should_package:
        zip_method = get_zip_method()
        bpl.console_utils.clear_console()
    else:
        zip_method = UserZipBuildMethod.DO_NOT_ZIP

    clear_old_files = get_clear_old_files()
    bpl.console_utils.clear_console()

    if should_package:
        launch = get_launch()
        bpl.console_utils.clear_console()
    else:
        launch = False


    platforms_list = build_platforms.get_platforms()
    build_modes_list = build_modes.get_build_modes()
    build_targets_list = build_targets.get_build_targets()


    build_config: RawBuildConfigStruct = RawBuildConfigStruct()
    build_config.clear_old_files = clear_old_files
    build_config.control_build_methods = control_build_methods
    for platform in platforms_list:
        for build_mode in build_modes_list:
            # Create task and add builds
            full_build_task = build_config.tasks.add_task()
            for build_target in build_targets_list:
                full_build_task.builds_config.add_new_build(platform, build_target, build_mode, should_package)
                if should_package:
                    full_build_task.post_build_config.rename_executable = True
                    full_build_task.post_build_config.set_all_file_actions(PostBuildFileAction.MOVE_OUTSIDE)
            # Add zip
            if should_package and len(build_targets_list) > 0:
                if zip_method.sperate_zips():
                    for build_target in build_targets_list:
                        full_build_task_zip = full_build_task.zip_config.add_zip(build_mode)
                        full_build_task_zip.use_single_format()
                        full_build_task_zip.add_build_to_zip(platform, build_target, zip_method.include_mods())
                        if zip_method.include_extracted_files():
                            full_build_task_zip.add_debug_files_to_zip(platform, build_target)
                            full_build_task_zip.add_mod_files_to_zip(platform, build_target)
                else:
                    full_build_task_zip = full_build_task.zip_config.add_zip(build_mode)
                    full_build_task_zip.use_single_format()
                    for build_target in build_targets_list:
                        full_build_task_zip.add_build_to_zip(platform, build_target, zip_method.include_mods())
                        if zip_method.include_extracted_files():
                            full_build_task_zip.add_debug_files_to_zip(platform, build_target)
                            full_build_task_zip.add_mod_files_to_zip(platform, build_target)
    if launch:
        if len(platforms_list) > 0 and len(build_targets_list) > 0 and len(build_modes_list) > 0:
            build_config.launch = LaunchBuildConfigStruct(platforms_list[0], build_targets_list[0], build_modes_list[0])

    return build_config