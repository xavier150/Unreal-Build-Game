from typing import List, Optional
from enum import Enum
from .build_types import BuildModeEnum, BuildPlatformEnum, BuildTargetEnum

class ControlBuildMethod(Enum):
    SEQUENTIAL = "Sequential"
    PARALLEL = "Parallel"

# OLD
class PackageBuildMethod(Enum):
    DO_NOT_PACKAGE = "DoNotPackage" # Build without packaging
    PACKAGE_ONLY = "PackageOnly" # Build and package
    PACKAGE_AND_ZIP = "PackageAndZip" # Build, package, and zip
    PACKAGE_AND_ZIP_WITH_MODS = "PackageAndZipWithMods" # Build, package, and zip including mod files (Debug only)
    PACKAGE_AND_ZIP_WITH_EXTRACTED_FILES = "PackageAndZipWithExtractedFiles" # Build, package, zip, and zip debug and mods files in separate zips



'''
# Build full config data strcuture
class UserBuildConfigStruct:
    def __init__(self):
        self.console_build_methods = ControlBuildMethod.SEQUENTIAL
        self.user_build_config = "Shipping"
        self.build_to_do = "Win64"
        self.build_targets = BuildTargets.CLIENT
        self.package_build_config = PackagesBuildConfiguration()
        self.clear_old_files = True
        self.launch_build_when_done = LaunchBuildWhenDone.DO_NOT_LAUNCH

    def set_config(
        self,
        console_build_methods: ControlBuildMethod,
        user_build_config: str,
        build_to_do: str,
        build_targets: BuildTargets,
        package_build_config: PackagesBuildConfiguration,
        clear_old_files: bool,
        launch_build_when_done: LaunchBuildWhenDone
    ) -> None:
        self.console_build_methods = console_build_methods
        self.user_build_config = user_build_config
        self.build_to_do = build_to_do
        self.build_targets = build_targets
        self.package_build_config = package_build_config
        self.clear_old_files = clear_old_files
        self.launch_build_when_done = launch_build_when_done

    def set_config_and_return(
        self,
        console_build_methods: ControlBuildMethod,
        user_build_config: str,
        build_to_do: str,
        build_targets: BuildTargets,
        package_build_config: PackagesBuildConfiguration,
        clear_old_files: bool,
        launch_build_when_done: LaunchBuildWhenDone
    ) -> "UserBuildConfigStruct":
        """Set config and return self for chaining."""
        self.set_config(
            console_build_methods=console_build_methods,
            user_build_config=user_build_config,
            build_to_do=build_to_do,
            build_targets=build_targets,
            package_build_config=package_build_config,
            clear_old_files=clear_old_files,
            launch_build_when_done=launch_build_when_done
        )
        return self
'''
    
################### -----------------------

class BuildConfiguration():
    def __init__(self):
        self.platform: BuildPlatformEnum = BuildPlatformEnum.WIN64
        self.build_target: BuildTargetEnum = BuildTargetEnum.CLIENT
        self.build_mode: BuildModeEnum = BuildModeEnum.SHIPPING
        self.should_package: bool = False
        self.fake_build: bool = False # If True, skip UAT and generate a dummy build folder instead

class BuildsConfiguration():
    def __init__(self):
        self.builds: List[BuildConfiguration] = []

    def add_new_build(
            self, 
            platform: BuildPlatformEnum, 
            build_target: BuildTargetEnum, 
            build_mode: BuildModeEnum,
            should_package: bool,
            fake_build: bool = False
        ) -> BuildConfiguration:

        new_build = BuildConfiguration()
        new_build.platform = platform
        new_build.build_target = build_target
        new_build.build_mode = build_mode
        new_build.should_package = should_package
        new_build.fake_build = fake_build
        self.builds.append(new_build)
        return new_build

class PostBuildFileAction(Enum):
    DO_NOTHING = "DoNothing"
    MOVE_OUTSIDE = "MoveOutside" # Move the file outside of the build folder
    COPY_OUTSIDE = "CopyOutside" # Copy the file outside of the build folder
    REMOVE = "Remove" # Remove the file

class PostBuildConfiguration():
    def __init__(self):
        self.rename_executable: bool = False
        self.manifest_file: PostBuildFileAction = PostBuildFileAction.DO_NOTHING
        self.debug_files: PostBuildFileAction = PostBuildFileAction.DO_NOTHING
        self.mod_files: PostBuildFileAction = PostBuildFileAction.DO_NOTHING

    def set_all_file_actions(self, action: PostBuildFileAction) -> None:
        self.manifest_file = action
        self.debug_files = action
        self.mod_files = action

class ZipBuildConfiguration():
    def __init__(
            self,
            platform: BuildPlatformEnum = BuildPlatformEnum.WIN64,
            build_target: BuildTargetEnum = BuildTargetEnum.CLIENT,
            include_modes: bool = False,
            extras_only: bool = False
        ):
        self.platform: BuildPlatformEnum = platform
        self.build_target: BuildTargetEnum = build_target
        self.include_modes: bool = include_modes
        self.extras_only: bool = extras_only # If True, only debug and/or mod files are zipped, not the main build folder
        self.debug_files_extra: bool = False # Only used when extras_only is True
        self.mod_files_extra: bool = False # Only used when extras_only is True
        self.mod_name_filters: Optional[List[str]] = None # Only used when mod_files_extra is True, e.g. ["pakchunk101", "pakchunk102"]

class ZipConfiguration():
    def __init__(
            self, 
            build_configurations: Optional[List[ZipBuildConfiguration]] = None,
        ):
        self.build_configurations = build_configurations if build_configurations is not None else []
        self.zip_file_name_format: str = self.get_single_format()
        self.zip_file_prefix: str = ""
        self.build_mode = BuildModeEnum.SHIPPING

    def add_build_to_zip(
            self, 
            platform: BuildPlatformEnum, 
            build_target: BuildTargetEnum, 
            include_modes: bool = False
        ) -> ZipBuildConfiguration:
        new_build_config = ZipBuildConfiguration(platform, build_target, include_modes)
        self.build_configurations.append(new_build_config)
        return new_build_config

    def add_debug_files_to_zip(self, platform: BuildPlatformEnum, build_target: BuildTargetEnum) -> ZipBuildConfiguration:
        """Adds only the debug files (including manifest files) of a build to the zip, without the main build folder."""
        new_build_config = ZipBuildConfiguration(platform, build_target, extras_only=True)
        new_build_config.debug_files_extra = True
        self.build_configurations.append(new_build_config)
        return new_build_config

    def add_mod_files_to_zip(self, platform: BuildPlatformEnum, build_target: BuildTargetEnum, mod_names: Optional[List[str]] = None) -> ZipBuildConfiguration:
        """Adds only the mod files of a build to the zip, without the main build folder.
        If mod_names is provided (e.g. ["pakchunk101", "pakchunk102"]), only mod files whose name starts with one of these are included."""
        new_build_config = ZipBuildConfiguration(platform, build_target, extras_only=True)
        new_build_config.mod_files_extra = True
        new_build_config.mod_name_filters = mod_names
        self.build_configurations.append(new_build_config)
        return new_build_config
    
    def get_single_format(self) -> str:
        return "{project_name} - {app_version} - {platform}.zip"
    
    def get_seperate_format(self) -> str:
        return "{project_name} - {app_version} - {platform}_{build_target}.zip"
    
    def use_single_format(self):
        self.zip_file_name_format = self.get_single_format()

    def use_seperate_format(self):
        self.zip_file_name_format = self.get_seperate_format()


    def set_prefix(self, prefix: str) -> None:
        """Sets a prefix prepended to the generated zip file name, e.g. 'TEST_'."""
        self.zip_file_prefix = prefix

    def get_zip_file_name(self, project_name: str, app_version: str) -> str:
        if len(self.build_configurations) > 0:
            formatted_name = self.zip_file_name_format.format(
                project_name=project_name,
                app_version=app_version,
                platform=self.build_configurations[0].platform.value,
                build_target=self.build_configurations[0].build_target.value
            )
            return f"{self.zip_file_prefix}{formatted_name}"
        else:
            return "Unknown.zip"
            
class ZipListConfiguration():
    def __init__(self):
        self.zip_list: List[ZipConfiguration] = []

    def add_zip(self, build_mode: BuildModeEnum) -> ZipConfiguration:
        new_zip_config = ZipConfiguration()
        new_zip_config.build_mode = build_mode
        self.zip_list.append(new_zip_config)
        return new_zip_config


class TaskConfigStruct:
    def __init__(
            self,
            builds_config: Optional[BuildsConfiguration] = None,
            post_build_config: Optional[PostBuildConfiguration] = None,
            zip_config: Optional[ZipListConfiguration] = None
        ):
        self.builds_config = builds_config if builds_config is not None else BuildsConfiguration()
        self.post_build_config = post_build_config if post_build_config is not None else PostBuildConfiguration()
        self.zip_config = zip_config if zip_config is not None else ZipListConfiguration()

class TasksConfigStruct:
    def __init__(
            self,
            tasks_list: Optional[List[TaskConfigStruct]] = None
        ):
        self.tasks_list = tasks_list if tasks_list is not None else []

    def add_task(self) -> TaskConfigStruct:
        new_task = TaskConfigStruct()
        self.tasks_list.append(new_task)
        return new_task

class LaunchBuildConfigStruct():
    def __init__(
            self,
            platform: BuildPlatformEnum,
            build_target: BuildTargetEnum,
            build_mode: BuildModeEnum
        ):
        self.platform: BuildPlatformEnum = platform
        self.build_target: BuildTargetEnum = build_target
        self.build_mode: BuildModeEnum = build_mode

class RawBuildConfigStruct:
    def __init__(
            self, 
            control_build_methods: ControlBuildMethod = ControlBuildMethod.SEQUENTIAL, 
            tasks: Optional[TasksConfigStruct] = None,
            launch: Optional[LaunchBuildConfigStruct] = None
        ):
        self.clear_old_files: bool = True
        self.control_build_methods: ControlBuildMethod = control_build_methods
        self.tasks: TasksConfigStruct = tasks if tasks is not None else TasksConfigStruct()
        self.launch: Optional[LaunchBuildConfigStruct] = launch


