import subprocess
import platform
from pathlib import Path

# Get script path and its directory
script_path = Path(__file__).resolve()
script_directory = script_path.parent.parent

run_devblog_manager = True
convert_current_post_files = False
compress_current_post_medias = False


if platform.system() == "Windows":
    script_to_call = script_directory / "run_mmvs_builder.py"
    python_cmd = "python"
else:
    script_to_call = script_directory / "run_mmvs_builder.py"
    # For Linux it use source ~/venv/bin/activate
    python_cmd = Path.home() / "venv" / "bin" / "python"

# Prepare arguments as strings
args = [
    str(script_to_call),
    str(script_directory),
    str(run_devblog_manager),
    str(convert_current_post_files),
    str(compress_current_post_medias)
]
subprocess.run([python_cmd] + args)