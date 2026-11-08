"""
Module to manage saving and loading of previous build configurations.
"""

import json
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, cast

from .build_config_type import (
    ControlBuildMethod,
    LaunchBuildConfigStruct,
    PostBuildFileAction,
    RawBuildConfigStruct,
)
from .build_types import BuildModeEnum, BuildPlatformEnum, BuildTargetEnum


CONFIG_SAVE_PATH = Path(tempfile.gettempdir()) / "mmvs_last_build_config.json"
CONFIG_VERSION = 1


class LastBuildConfig:
    """Class to manage saving and loading of the last build configuration."""

    @staticmethod
    def _enum_value(enum_obj: Any) -> Any:
        return enum_obj.value if hasattr(enum_obj, "value") else enum_obj

    @staticmethod
    def _parse_enum(enum_type: Any, value: Any, default: Any) -> Any:
        try:
            return enum_type(value)
        except Exception:
            return default

    @staticmethod
    def _safe_bool(value: Any, default: bool = False) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return default
        return bool(value)

    @staticmethod
    def save_build_config(config: RawBuildConfigStruct) -> None:
        """Save the build configuration to a JSON file."""
        try:
            config_data: Dict[str, Any] = {
                "version": CONFIG_VERSION,
                "clear_old_files": LastBuildConfig._safe_bool(getattr(config, "clear_old_files", True), True),
                "control_build_methods": LastBuildConfig._enum_value(getattr(config, "control_build_methods", ControlBuildMethod.SEQUENTIAL)),
                "tasks": [],
                "launch": None,
            }

            for task in getattr(getattr(config, "tasks", None), "tasks_list", []):
                serialized_task: Dict[str, Any] = {
                    "builds": [],
                    "post_build_config": {
                        "rename_executable": LastBuildConfig._safe_bool(
                            getattr(getattr(task, "post_build_config", None), "rename_executable", False),
                            False,
                        ),
                        "manifest_file": LastBuildConfig._enum_value(
                            getattr(getattr(task, "post_build_config", None), "manifest_file", PostBuildFileAction.DO_NOTHING)
                        ),
                        "debug_files": LastBuildConfig._enum_value(
                            getattr(getattr(task, "post_build_config", None), "debug_files", PostBuildFileAction.DO_NOTHING)
                        ),
                        "mod_files": LastBuildConfig._enum_value(
                            getattr(getattr(task, "post_build_config", None), "mod_files", PostBuildFileAction.DO_NOTHING)
                        ),
                    },
                    "zip_list": [],
                }

                for build in getattr(getattr(task, "builds_config", None), "builds", []):
                    serialized_task["builds"].append(
                        {
                            "platform": LastBuildConfig._enum_value(getattr(build, "platform", BuildPlatformEnum.WIN64)),
                            "build_target": LastBuildConfig._enum_value(getattr(build, "build_target", BuildTargetEnum.CLIENT)),
                            "build_mode": LastBuildConfig._enum_value(getattr(build, "build_mode", BuildModeEnum.SHIPPING)),
                            "should_package": LastBuildConfig._safe_bool(getattr(build, "should_package", False), False),
                        }
                    )

                for zip_item in getattr(getattr(task, "zip_config", None), "zip_list", []):
                    serialized_zip: Dict[str, Any] = {
                        "build_mode": LastBuildConfig._enum_value(getattr(zip_item, "build_mode", BuildModeEnum.SHIPPING)),
                        "zip_file_name_format": getattr(zip_item, "zip_file_name_format", ""),
                        "build_configurations": [],
                    }

                    for zip_build_config in getattr(zip_item, "build_configurations", []):
                        serialized_zip["build_configurations"].append(
                            {
                                "platform": LastBuildConfig._enum_value(getattr(zip_build_config, "platform", BuildPlatformEnum.WIN64)),
                                "build_target": LastBuildConfig._enum_value(getattr(zip_build_config, "build_target", BuildTargetEnum.CLIENT)),
                                "include_modes": LastBuildConfig._safe_bool(getattr(zip_build_config, "include_modes", False), False),
                                "extras_only": LastBuildConfig._safe_bool(getattr(zip_build_config, "extras_only", False), False),
                                "debug_files_extra": LastBuildConfig._safe_bool(getattr(zip_build_config, "debug_files_extra", False), False),
                                "mod_files_extra": LastBuildConfig._safe_bool(getattr(zip_build_config, "mod_files_extra", False), False),
                            }
                        )

                    serialized_task["zip_list"].append(serialized_zip)

                config_data["tasks"].append(serialized_task)

            if getattr(config, "launch", None) is not None:
                if config.launch:
                    config_data["launch"] = {
                        "platform": LastBuildConfig._enum_value(config.launch.platform),
                        "build_target": LastBuildConfig._enum_value(config.launch.build_target),
                        "build_mode": LastBuildConfig._enum_value(config.launch.build_mode),
                    }
                else:
                    config_data["launch"] = None

            with open(CONFIG_SAVE_PATH, "w", encoding="utf-8") as file_handle:
                json.dump(config_data, file_handle, indent=2, ensure_ascii=False)

            print("✓ Build configuration saved")
        except Exception as error:
            print(f"⚠ Error saving configuration: {error}")

    @staticmethod
    def load_build_config_json() -> Optional[Dict[str, Any]]:
        """Load the raw configuration JSON file."""
        if not CONFIG_SAVE_PATH.exists():
            return None

        try:
            with open(CONFIG_SAVE_PATH, "r", encoding="utf-8") as file_handle:
                loaded_data: Any = json.load(file_handle)
                if isinstance(loaded_data, dict):
                    return cast(Dict[str, Any], loaded_data)
                return None
        except Exception as error:
            print(f"⚠ Error reading configuration: {error}")
            return None

    @staticmethod
    def load_config_struct() -> Optional[RawBuildConfigStruct]:
        """Load the last build configuration and return it as RawBuildConfigStruct."""
        config_data = LastBuildConfig.load_build_config_json()
        if config_data is None:
            return None

        try:
            build_config = RawBuildConfigStruct()
            build_config.clear_old_files = LastBuildConfig._safe_bool(config_data.get("clear_old_files"), True)
            build_config.control_build_methods = LastBuildConfig._parse_enum(
                ControlBuildMethod,
                config_data.get("control_build_methods"),
                ControlBuildMethod.SEQUENTIAL,
            )

            for task_data in config_data.get("tasks", []):
                task_data = cast(Dict[str, Any], task_data)

                task = build_config.tasks.add_task()

                for build_data in task_data.get("builds", []):
                    build_data = cast(Dict[str, Any], build_data)

                    platform = LastBuildConfig._parse_enum(
                        BuildPlatformEnum,
                        build_data.get("platform"),
                        BuildPlatformEnum.WIN64,
                    )
                    build_target = LastBuildConfig._parse_enum(
                        BuildTargetEnum,
                        build_data.get("build_target"),
                        BuildTargetEnum.CLIENT,
                    )
                    build_mode = LastBuildConfig._parse_enum(
                        BuildModeEnum,
                        build_data.get("build_mode"),
                        BuildModeEnum.SHIPPING,
                    )
                    should_package = LastBuildConfig._safe_bool(build_data.get("should_package"), False)

                    task.builds_config.add_new_build(platform, build_target, build_mode, should_package)

                post_build_data = cast(Dict[str, Any], task_data.get("post_build_config", {}))
                task.post_build_config.rename_executable = LastBuildConfig._safe_bool(
                    post_build_data.get("rename_executable"),
                    False,
                )
                task.post_build_config.manifest_file = LastBuildConfig._parse_enum(
                    PostBuildFileAction,
                    post_build_data.get("manifest_file"),
                    PostBuildFileAction.DO_NOTHING,
                )
                task.post_build_config.debug_files = LastBuildConfig._parse_enum(
                    PostBuildFileAction,
                    post_build_data.get("debug_files"),
                    PostBuildFileAction.DO_NOTHING,
                )
                task.post_build_config.mod_files = LastBuildConfig._parse_enum(
                    PostBuildFileAction,
                    post_build_data.get("mod_files"),
                    PostBuildFileAction.DO_NOTHING,
                )

                for zip_data in task_data.get("zip_list", []):
                    zip_data = cast(Dict[str, Any], zip_data)

                    zip_mode = LastBuildConfig._parse_enum(
                        BuildModeEnum,
                        zip_data.get("build_mode"),
                        BuildModeEnum.SHIPPING,
                    )
                    zip_entry = task.zip_config.add_zip(zip_mode)

                    zip_file_name_format = zip_data.get("zip_file_name_format")
                    if isinstance(zip_file_name_format, str) and len(zip_file_name_format) > 0:
                        zip_entry.zip_file_name_format = zip_file_name_format

                    for zip_build_data in zip_data.get("build_configurations", []):
                        zip_build_data = cast(Dict[str, Any], zip_build_data)

                        zip_platform = LastBuildConfig._parse_enum(
                            BuildPlatformEnum,
                            zip_build_data.get("platform"),
                            BuildPlatformEnum.WIN64,
                        )
                        zip_target = LastBuildConfig._parse_enum(
                            BuildTargetEnum,
                            zip_build_data.get("build_target"),
                            BuildTargetEnum.CLIENT,
                        )
                        include_modes = LastBuildConfig._safe_bool(zip_build_data.get("include_modes"), False)
                        extras_only = LastBuildConfig._safe_bool(zip_build_data.get("extras_only"), False)
                        debug_files_extra = LastBuildConfig._safe_bool(zip_build_data.get("debug_files_extra"), False)
                        mod_files_extra = LastBuildConfig._safe_bool(zip_build_data.get("mod_files_extra"), False)

                        if extras_only:
                            if debug_files_extra:
                                zip_entry.add_debug_files_to_zip(zip_platform, zip_target)
                            if mod_files_extra:
                                zip_entry.add_mod_files_to_zip(zip_platform, zip_target)
                        else:
                            zip_entry.add_build_to_zip(
                                zip_platform,
                                zip_target,
                                include_modes,
                            )

            launch_data_raw = config_data.get("launch")
            if launch_data_raw is not None:
                launch_data = cast(Dict[str, Any], launch_data_raw)
                launch_platform = LastBuildConfig._parse_enum(
                    BuildPlatformEnum,
                    launch_data.get("platform"),
                    BuildPlatformEnum.WIN64,
                )
                launch_target = LastBuildConfig._parse_enum(
                    BuildTargetEnum,
                    launch_data.get("build_target"),
                    BuildTargetEnum.CLIENT,
                )
                launch_mode = LastBuildConfig._parse_enum(
                    BuildModeEnum,
                    launch_data.get("build_mode"),
                    BuildModeEnum.SHIPPING,
                )
                build_config.launch = LaunchBuildConfigStruct(launch_platform, launch_target, launch_mode)

            return build_config
        except Exception as error:
            print(f"⚠ Error converting configuration: {error}")
            return None
