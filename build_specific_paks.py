# Build only specific pak chunks with UnrealPak, from already cooked/staged data.
# Usage:
#   python build_specific_paks.py              -> iterative cook, then pak
#   python build_specific_paks.py --skip-cook  -> pak only (uses existing cooked data)

import argparse
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------- config

ENGINE_ROOT = Path(r"M:\MMVS_EngineFiles_v2")
PROJECT_FILE = Path(r"M:\MMVS_ProjectFiles_v2\UnrealProject\MacroMicroVrService.uproject")

CHUNKS = [103, 113]

# cooked/staged platform name -> UAT target platform name
PLATFORMS = {
    "Windows": "Win64",
    "Linux": "Linux",
}
COMPRESS = True

# Where the generated .pak files are copied
OUTPUT_DIR = Path(r"F:\MMVS_GameBuilds\SpecificPaks")

# ---------------------------------------------------------------- paths

PROJECT_ROOT = PROJECT_FILE.parent
UNREAL_PAK = ENGINE_ROOT / "Engine" / "Binaries" / "Win64" / "UnrealPak.exe"
RUN_UAT = ENGINE_ROOT / "Engine" / "Build" / "BatchFiles" / "RunUAT.bat"
# UAT writes the UnrealPak response files here during the stage step
RESPONSE_FILES = (
    ENGINE_ROOT / "Engine" / "Programs" / "AutomationTool" / "Saved" / "ResponseFiles"
)


def crypto_json(platform: str) -> Path:
    return (
        PROJECT_ROOT / "Saved" / "Cooked" / platform / PROJECT_FILE.stem
        / "Metadata" / "Crypto.json"
    )


def run(command: list[str]) -> None:
    print("RUN:", " ".join(str(c) for c in command))
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"ERROR: command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def cook_iterative() -> None:
    target_platforms = "+".join(PLATFORMS.values())
    run([
        str(RUN_UAT),
        "BuildCookRun",
        f"-project={PROJECT_FILE}",
        f"-targetplatform={target_platforms}",
        "-noP4",
        "-nocompileeditor",
        "-cook",
        "-iterativecooking",
        "-skipbuild",
        "-skipstage",
        "-clientconfig=Shipping",
    ])


def build_pak(chunk: int, platform: str) -> Path:
    pak_list = RESPONSE_FILES / f"PakList_pakchunk{chunk}-{platform}.txt"
    if not pak_list.is_file():
        print(f"ERROR: pak list not found: {pak_list}")
        print("You need at least one full staged build so UAT generates the PakList files.")
        sys.exit(1)

    output_pak = OUTPUT_DIR / f"pakchunk{chunk}-{platform}.pak"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    command = [
        str(UNREAL_PAK),
        str(output_pak),
        f"-Create={pak_list}",
        f"-platform={platform}",
    ]
    if COMPRESS:
        command.append("-compress")
    crypto = crypto_json(platform)
    if crypto.is_file():
        command.append(f"-cryptokeys={crypto}")
        # bEnablePakSigning=True in DefaultCrypto.ini -> generate the .sig file
        command.append("-sign")

    run(command)
    return output_pak


def main() -> None:
    parser = argparse.ArgumentParser(description="Build specific pak chunks only.")
    parser.add_argument("--skip-cook", action="store_true", help="skip the iterative cook and pak from existing cooked data")
    args = parser.parse_args()

    if not UNREAL_PAK.is_file():
        print(f"ERROR: UnrealPak not found: {UNREAL_PAK}")
        sys.exit(1)

    if not args.skip_cook:
        cook_iterative()

    built = [
        build_pak(chunk, platform)
        for platform in PLATFORMS
        for chunk in CHUNKS
    ]

    print("\nDone. Generated paks:")
    for pak in built:
        print(" -", pak)
    print("\nCopy them into: <Game>\\MacroMicroVrService\\Content\\Paks\\")


if __name__ == "__main__":
    main()
