import shutil
from datetime import datetime
from typing import List, Any, Optional
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from . import bpl
from . import config
from . import user_input
from . import make_user_config_build
from .Tasks.GroupedUat import run_builds_class as run_builds
from .Tasks.GroupedUat.run_builds_class import GroupedBuildTask
from .Tasks.Base.build_task_base import BuildTaskBase
from . import run_builded_package
from . import brut_force_project_rebuild
from . import console_ui
from . import build_config_type
from .build_config_type import RawBuildConfigStruct
from .build_types import BuildTargetEnum
from . import project_version_utils
from . import additional_build_files
from . import build_config_manager
from . import file_naming


# Global semaphore to limit simultaneous Unreal builds
# Unreal Engine cannot perform multiple builds at the same time
UNREAL_BUILD_SEMAPHORE = threading.Semaphore(config.max_concurrent_unreal_builds)



def show_build_info():
    app_version = project_version_utils.get_project_version()
    human_readable_version = project_version_utils.get_human_readable_project_version()
    print(f"Project Version: {app_version}")
    print(f"Human Readable Version: {human_readable_version}")
    print("")

def get_user_config() -> Optional[RawBuildConfigStruct]:

    build_config: RawBuildConfigStruct = RawBuildConfigStruct()
    preset_build_config: str = ""

    # Get the user's choice (Custom, AsBefore, or Preset)
    preset_build_config = user_input.get_build_config()
    bpl.console_utils.clear_console()
    
    if preset_build_config == "Custom":
        build_config = make_user_config_build.make_user_config_build()
        bpl.console_utils.clear_console()

    elif preset_build_config == "AsBefore":        
        print("📋 Loading last configuration...")
        new_build_config = build_config_manager.LastBuildConfig.load_config_struct()
        if new_build_config:
            build_config = new_build_config
        else:
            print("⚠ Error loading last configuration. Please create a build with 'Custom' first")
            return None

    else:
        # It's a preset
        preset_config = config.get_preset_config(preset_build_config)
        if preset_config:
            build_config = preset_config
            print(f"✓ Preset loaded")
        else:
            print(f"⚠ Unknown preset: {preset_build_config}")
            return None
    return build_config


def clean_build_folder() -> bool:
    output_directory = Path(config.output_directory_path)
    print("Cleaning build folder at", output_directory)
    
    # Check if directory exists
    if output_directory.exists():
        try:
            # Delete all content of the folder
            for item in output_directory.iterdir():
                if item.name == config.uat_logs_folder_name:
                    continue
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            return True
        except Exception as e:
            print(bpl.color_set.red(f"Error while cleaning build folder: {e}"))
            return False
    return True

def create_pipeline_journal() -> BuildTaskBase:
    log_directory = config.output_directory_path / config.uat_logs_folder_name
    log_directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    journal = BuildTaskBase()
    journal.pipeline_log_path = log_directory / f"BUILD_{timestamp}.log"
    journal.write_pipeline_log(f"Project: {config.project_path}")
    journal.write_pipeline_log(f"Engine: {config.engine_folder_path}")
    print(f"Build pipeline log: {journal.pipeline_log_path}")
    return journal


def do_build(
    build_config: RawBuildConfigStruct,
    journal: Optional[BuildTaskBase] = None,
) -> List[GroupedBuildTask]:
    if journal is None:
        journal = create_pipeline_journal()
    with journal.log_step("TOTAL BUILD (excludes game runtime)"):
        builders = _do_build(build_config, journal)
        successful = bool(builders) and all(build.success for build in builders)
        journal.write_pipeline_log(f"BUILD RESULT: success={successful}")
        return builders


def _do_build(
    build_config: RawBuildConfigStruct, journal: BuildTaskBase,
) -> List[GroupedBuildTask]:

    timer = bpl.utils.CounterTimer()

    # Set control build method
    if build_config.control_build_methods.value == build_config_type.ControlBuildMethod.SEQUENTIAL.value:
        print("Running builds in sequential mode (series with all logs)...")
        use_parallel_builds = False
        use_progress_ui = False
    elif build_config.control_build_methods.value == build_config_type.ControlBuildMethod.PARALLEL.value:
        print("Running builds in parallel mode (progress UI)...")
        use_parallel_builds = True
        use_progress_ui = True
    else:
        raise ValueError("Invalid build control method")
    
    print_logs = not use_progress_ui # Avoid logs when use progress UI


    '''
    build_modes: List[BuildModeEnum] = []
    if(build_config.user_build_config == "All"):
        for config_enum in BuildModeEnum.get_all_valid_configs():
            build_modes.append(config_enum)
    else:
        build_modes.append(BuildModeEnum(build_config.user_build_config))
        



    builder_list: List[GroupedBuildTask] = run_all_builds(
        build_to_do=build_config.build_to_do, 
        create_client_build=build_config.build_targets.includes_client(), 
        create_server_build=build_config.build_targets.includes_server(), 
        package_build_method=build_config.package_build_method, 
        include_client_files=build_config.build_targets.includes_client(), 
        include_server_files=build_config.build_targets.includes_server(), 
        build_configs=build_modes, 
        clear_old_files=build_config.clear_old_files, 
        use_parallel_builds=use_parallel_builds, 
        use_progress_ui=use_progress_ui
    )       
    '''


    if (build_config.clear_old_files):
        with journal.log_step("CLEAN OUTPUT (preserve UAT_LOGS)"):
            success = clean_build_folder()
            journal.write_pipeline_log(f"CLEAN RESULT: success={success}")
        if not success:
            print(bpl.color_set.red("Failed to clean build folder, aborting build process"))
            return []
        
    # Initialiser le semaphore Unreal dans le module run_builds
    run_builds.set_unreal_build_semaphore(UNREAL_BUILD_SEMAPHORE)

    # Setup builder list
    builder_list: List[GroupedBuildTask] = []

    for task in build_config.tasks.tasks_list:
        grouped_uat_builder = GroupedBuildTask()
        grouped_uat_builder.print_logs = print_logs
        # Add Builder
        for build in task.builds_config.builds:
            build_output_directory = config.output_directory_path / build.build_mode.get_output_folder_name()

            new_sequential_build = grouped_uat_builder.new_sequential_build()
            new_builder = new_sequential_build.uat_builder
            new_builder.print_logs = print_logs
            new_builder.target_platform = build.platform.value
            new_builder.package = build.should_package
            new_builder.should_archive = build.should_package
            new_builder.archive_directory = build_output_directory
            new_builder.use_fake_directory_build = build.fake_build
            new_builder.client_config = build.build_mode.value
            new_builder.server_config = build.build_mode.value
            if build.build_target == BuildTargetEnum.SERVER:
                new_builder.noclient = True
                new_builder.server = True
                new_builder.server_platform = build.platform.value
            else:
                new_builder.platform = build.platform.value

            # Configure the post build action for this specific build
            new_post_build_action = new_sequential_build.post_build_action
            new_post_build_action.print_logs = print_logs
            new_post_build_action.is_server = build.build_target == BuildTargetEnum.SERVER
            new_post_build_action.rename_executable = task.post_build_config.rename_executable
            new_post_build_action.manifest_file = task.post_build_config.manifest_file
            new_post_build_action.debug_files = task.post_build_config.debug_files
            new_post_build_action.mod_files = task.post_build_config.mod_files

        # Add Zip Builder
        for zip in task.zip_config.zip_list:
            zip_output_directory = config.output_directory_path / zip.build_mode.get_output_folder_name()
            app_version = str(project_version_utils.get_human_readable_project_version(include_dash=False))
            zip_destination_file: Path = zip_output_directory / zip.get_zip_file_name(config.project_name, app_version)
            new_zip_builder = grouped_uat_builder.new_zip_builder()
            new_zip_builder.print_logs = print_logs
            new_zip_builder.zip_destination_file = zip_destination_file
            for zip_build_config in zip.build_configurations:
                # Add build to zip builder
                is_server = zip_build_config.build_target.value == BuildTargetEnum.SERVER.value
                platform_folder_name = zip_build_config.platform.get_default_platforms_folder(is_server)

                if not zip_build_config.extras_only:
                    data_path = zip_output_directory / platform_folder_name
                    data_folder = zip_build_config.platform.get_desired_build_folder(is_server)
                    new_zip_builder.folder_paths_to_include.append((data_folder, data_path, None))

                    # Add mods to zip builder if needed
                    if zip_build_config.include_modes:
                        mod_data_path = zip_output_directory / (platform_folder_name + config.mod_folder_suffix)
                        new_zip_builder.folder_paths_to_include.append((data_folder, mod_data_path, None))
                else:
                    # Add debug files (includes manifest files) to the zip in their own top-level folder
                    if zip_build_config.debug_files_extra:
                        debug_data_path = zip_output_directory / (platform_folder_name + config.debug_folder_suffix)
                        new_zip_builder.folder_paths_to_include.append((platform_folder_name + config.debug_folder_suffix, debug_data_path, None))

                    # Add mod files to the zip in their own top-level folder
                    if zip_build_config.mod_files_extra:
                        mod_data_path = zip_output_directory / (platform_folder_name + config.mod_folder_suffix)
                        new_zip_builder.folder_paths_to_include.append((platform_folder_name + config.mod_folder_suffix, mod_data_path, zip_build_config.mod_name_filters))

        if journal.pipeline_log_path is not None:
            grouped_uat_builder.set_pipeline_log_path(journal.pipeline_log_path)
        builder_list.append(grouped_uat_builder)

    # Run all builds
    progress_thread: Optional[threading.Thread] = None
    if use_progress_ui:
        progress_thread = console_ui.dynamic_console_ui.run_dynamic_console_ui(builder_list)

    if use_parallel_builds:
        print(f"Starting {len(builder_list)} builds in parallel...")
        with ThreadPoolExecutor(max_workers=len(builder_list)) as executor:
            futures: List[Any] = []
            for build in builder_list:
                future = executor.submit(build.run_all_builds)
                futures.append(future)
            
            # Attendre que tous les builds se terminent
            for future in futures:
                future.result()  # This will raise an exception if the build fails

        # Wait for dynamic display to finish (to ensure everything is properly displayed)
        if use_progress_ui and progress_thread:
            progress_thread.join()
    else:
        print(f"Starting {len(builder_list)} builds in series...")
        for build in builder_list:
            build.run_all_builds()
        if use_progress_ui and progress_thread:
            progress_thread.join()
    
    print("All tasks completed in", timer.get_str_time() )
    return builder_list

def run_build_launch(build_config: RawBuildConfigStruct):
    if build_config.launch:
        build_output_directory = config.output_directory_path / build_config.launch.build_mode.get_output_folder_name()
        exec_path = Path(build_output_directory) / build_config.launch.platform.get_default_platforms_folder(False) / file_naming.get_renamed_executable_name(build_config.launch.platform, False)
        if exec_path.exists():
            run_builded_package.launch_executable(exec_path)
        else:
            print(bpl.color_set.red(f"Executable not found at {exec_path}, cannot launch the game"))
        return


    print(bpl.color_set.red("Build failed, skipping run tasks..."))

def run_brut_force_project_rebuild():
    brut_force_project_rebuild.start_user_ui()

# Main function
def main():

    ## DEBUG
    if config.debug_launch_build:
        run_builded_package.launch_executable(config.debug_launch_build_executable_path)
        return
    # END DEBUG

    
    bpl.console_utils.clear_console()
    print("Starting MMVS UAT...")
    show_build_info()
    additional_build_files.check_and_init.init_additional_build_files_folder()

    build_config = get_user_config()
    if build_config is None:
        print(bpl.color_set.red("No valid build configuration, exiting..."))
        return
    
    # Save configuration
    build_config_manager.LastBuildConfig.save_build_config(build_config)
    
    journal = create_pipeline_journal()
    builder_list = do_build(build_config, journal)
    if build_config.launch and builder_list:
        with journal.log_step("LAUNCH AND GAME SESSION (includes game runtime)"):
            run_build_launch(build_config)

    # @TODO: Add an user input to ask if the user want to run the brut force project rebuild
    # run_brut_force_project_rebuild()
