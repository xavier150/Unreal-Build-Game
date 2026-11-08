import configparser
import re
from . import unreal_engine_path
from . import bpl


def get_project_version() -> str:
    project_directory_path = unreal_engine_path.get_project_directory_path()
    default_game_file = project_directory_path / "Config" / "DefaultGame.ini"
    if not default_game_file.exists():
        raise FileNotFoundError(f"DefaultGame.ini not found at {default_game_file}")
    else:
        config_parser = configparser.ConfigParser(strict=False)
        config_parser.read(default_game_file)
        version = config_parser.get('/Script/EngineSettings.GeneralProjectSettings', 'ProjectVersion')
        return version

def get_matcher_app_version():
    """
    MMVS versioning:
    [RELEASE].[MAJOR].[MILESTONE].[PATCH]-[PHASE][ITERATION]
    PHASE { pa, ap, a, b, rc, r }
    ITERATION = optional digits (e.g., ap19, rc2)
    More details: https://github.com/xavier150/MMVS/wiki/Versioning
    """
    project_version = get_project_version()
    # Pattern: [digits.digits.digits.digits] - [phase] [iteration?]
    # Group 1 = numeric version, Group 2 = phase, Group 3 = optional iteration (digits)
    pattern = r"(\d+\.\d+\.\d+\.\d+)(?:-(pa|ap|a|b|rc|r)(\d+)?)?"
    return re.search(pattern, project_version)

def is_valid_app_version() -> bool:
    """
    Vérifie si la version du projet correspond au format attendu.
    """
    matcher = get_matcher_app_version()
    return matcher is not None

def get_human_readable_project_version(include_dash: bool = True) -> str:
    """
    Retourne une version lisible par l'homme au format MMVS.
    """
    matcher = get_matcher_app_version()
    
    if not matcher:
        text = f"GetHumanReadableAppVersion: Version string '{get_project_version()}' does not match expected format."
        print(bpl.color_set.red(text))
        return "Error format readable version"
    
    version_number = matcher.group(1)  # "0.4.0.1"
    # Crop to tree number if last number is zero (e.g., "0.4.6.0" -> "0.4.6")
    if version_number.endswith(".0"):
        version_number = version_number[:-2]
    phase_code = matcher.group(2) if matcher.group(2) else ""  # "ap", "a", "b", "rc", "r", "pa" or empty
    iteration = matcher.group(3) if matcher.group(3) else ""  # "19", "2", or empty
    
    # Map phase codes to human-readable text
    phase_mapping = {
        "pa": "Pre-Alpha",
        "ap": "Alpha Preview",
        "a": "Alpha",
        "b": "Beta",
        "rc": "Release Candidate",
        "r": "Release"
    }
    
    if phase_code and phase_code not in phase_mapping:
        text = f"GetHumanReadableAppVersion: Unrecognized phase code '{phase_code}' in version string '{get_project_version()}'."
        print(bpl.color_set.red(text))
        return "Error format readable version"
    
    # Build final display string
    display_version = f"v{version_number}"
    
    if phase_code:
        phase_text = phase_mapping[phase_code]
        if include_dash:
            display_version += f" - {phase_text}"
        else:
            display_version += f" {phase_text}"

        # Append iteration number when present.
        # For "ap", "b" and "rc" we show the counter (e.g., "Alpha Preview 19", "Beta 3", "Release Candidate 2").
        if iteration and phase_code in ["ap", "b", "rc"]:
            display_version += f" {iteration}"
        # For "pa", "a", "r" iteration is typically omitted by spec.
    
    return display_version
