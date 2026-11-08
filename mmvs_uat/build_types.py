from enum import Enum
from typing import List


class BuildPlatformEnum(Enum):
    WIN64 = "Win64"
    LINUX = "Linux"
    LINUX_ARM64 = "LinuxArm64"

    @staticmethod
    def get_all_valid_platforms() -> List["BuildPlatformEnum"]:
        return [BuildPlatformEnum.WIN64, BuildPlatformEnum.LINUX, BuildPlatformEnum.LINUX_ARM64]

    def get_friendly_name(self):
        if self.value == BuildPlatformEnum.WIN64.value:
            return "Windows 64-bit"
        elif self.value == BuildPlatformEnum.LINUX.value:
            return "Linux"
        elif self.value == BuildPlatformEnum.LINUX_ARM64.value:
            return "Linux ARM64"
        else:
            return "Invalid Platform"
        
    def get_default_platforms_folder(self, is_server: bool=False) -> str:
        if is_server:
            if self.value == BuildPlatformEnum.WIN64.value:
                return "WindowsServer"
            elif self.value == BuildPlatformEnum.LINUX.value:
                return "LinuxServer"
            elif self.value == BuildPlatformEnum.LINUX_ARM64.value:
                return "LinuxArm64Server"
        else:
            if self.value == BuildPlatformEnum.WIN64.value:
                return "Windows"
            elif self.value == BuildPlatformEnum.LINUX.value:
                return "Linux"
            elif self.value == BuildPlatformEnum.LINUX_ARM64.value:
                return "LinuxArm64"
        return "InvalidPlatformFolder"
    
    def get_build_name(self, server: bool = False) -> str:
        if server:
            if self.value == BuildPlatformEnum.WIN64.value:
                return "(Server Win64)"
            elif self.value == BuildPlatformEnum.LINUX.value:
                return "(Server Linux)"
            elif self.value == BuildPlatformEnum.LINUX_ARM64.value:
                return "(Server LinuxArm64)"
        else:
            if self.value == BuildPlatformEnum.WIN64.value:
                return "(Game Win64)"
            elif self.value == BuildPlatformEnum.LINUX.value:
                return "(Game Linux)"
            elif self.value == BuildPlatformEnum.LINUX_ARM64.value:
                return "(Game LinuxArm64)"
        return "InvalidBuildName"

    def get_executable_file_name(self, base_name: str) -> str:
        """Adds the platform suffix/extension to an executable base name (e.g. "TagGame" -> "TagGame-Arm64.sh")."""
        if self.value == BuildPlatformEnum.WIN64.value:
            return f"{base_name}.exe"
        elif self.value == BuildPlatformEnum.LINUX.value:
            return f"{base_name}.sh"
        elif self.value == BuildPlatformEnum.LINUX_ARM64.value:
            return f"{base_name}-Arm64.sh"
        return "InvalidExecutable"

    def get_desired_build_folder(self, server: bool = False) -> str:
        if server:
            if self.value == BuildPlatformEnum.WIN64.value:
                return "WindowsServer"
            elif self.value == BuildPlatformEnum.LINUX.value:
                return "LinuxServer"
            elif self.value == BuildPlatformEnum.LINUX_ARM64.value:
                return "LinuxArm64Server"
        else:
            if self.value == BuildPlatformEnum.WIN64.value:
                return "WindowsGame"
            elif self.value == BuildPlatformEnum.LINUX.value:
                return "LinuxGame"
            elif self.value == BuildPlatformEnum.LINUX_ARM64.value:
                return "LinuxArm64Game"
        return "InvalidBuildFolder"

class BuildTargetEnum(Enum):
    CLIENT = "Client"
    SERVER = "Server"

class BuildModeEnum(Enum):
    DEBUG_GAME = "DebugGame"
    DEVELOPMENT = "Development"
    SHIPPING = "Shipping"

    @staticmethod
    def get_all_valid_configs() -> List["BuildModeEnum"]:
        configs: List[BuildModeEnum] = [
            BuildModeEnum.DEBUG_GAME,
            BuildModeEnum.DEVELOPMENT,
            BuildModeEnum.SHIPPING,
        ]
        return configs

    @staticmethod
    def get_all_valid_configs_values() -> List[str]:
        config_values: List[str] = [
            BuildModeEnum.DEBUG_GAME.value,
            BuildModeEnum.DEVELOPMENT.value,
            BuildModeEnum.SHIPPING.value,
        ]
        return config_values

    def get_friendly_name(self):
        if self.value == BuildModeEnum.DEBUG_GAME.value:
            return "Debug Game"
        elif self.value == BuildModeEnum.DEVELOPMENT.value:
            return "Development"
        elif self.value == BuildModeEnum.SHIPPING.value:
            return "Shipping"
        else:
            return "Invalid Build Config"
        
    def get_output_folder_name(self) -> str:
        if self.value == BuildModeEnum.DEBUG_GAME.value:
            return "DebugGame"
        elif self.value == BuildModeEnum.DEVELOPMENT.value:
            return "Development"
        elif self.value == BuildModeEnum.SHIPPING.value:
            return "Shipping"
        else:
            return "UnknownBuildConfig"
        
    def get_build_version_type(self) -> str:
        if self.value == BuildModeEnum.DEBUG_GAME.value:
            return "Debug"
        elif self.value == BuildModeEnum.DEVELOPMENT.value:
            return "Development"
        elif self.value == BuildModeEnum.SHIPPING.value:
            return "Shipping"
        else:
            return "Unknown"