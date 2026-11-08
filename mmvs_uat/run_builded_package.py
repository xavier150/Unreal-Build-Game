import subprocess
import sys
from pathlib import Path


def launch_executable(executable_path: Path):

    # Prevent obvious cross-platform launch errors (e.g. Linux .sh on Windows).
    if sys.platform.startswith("win") and executable_path.suffix.lower() == ".sh":
        print(
            f"Skipping launch: '{executable_path}' is a Linux shell script and cannot run directly on Windows."
        )
        return False

    try:
        print(f"Launching executable at {str(executable_path)}...")
        subprocess.Popen(
            [str(executable_path), "-log"],  # '-log' force Unreal à ouvrir sa fenêtre de console
            cwd=executable_path.parent
        ).communicate()
        print(f"Executable '{executable_path}' Finished running.")
        return True
    
    except OSError as error:
        print(f"Failed to launch executable '{executable_path}': {error}")
        return False
    except Exception as error:
        print(f"Unexpected error while launching '{executable_path}': {error}")
        return False
    
    '''
    When launching from VSCode on windows without the ".communicate()" the game don't found the main GPU!
    '''

    '''
    Normal use:

[2026.02.18-14.24.35:250][  0]LogD3D12RHI: Aftermath initialized
[2026.02.18-14.24.35:250][  0]LogD3D12RHI: Loading WinPixEventRuntime.dll for PIX profiling (from ../../../Engine/Binaries/ThirdParty/Windows/WinPixEventRuntime/x64).
[2026.02.18-14.24.35:250][  0]LogRHI: Checking if RHI D3D12 with Feature Level SM6 is supported by your system.
[2026.02.18-14.24.35:446][  0]LogD3D12RHI: Found D3D12 adapter 0: NVIDIA GeForce RTX 5090 (VendorId: 10de, DeviceId: 2b85, SubSysId: 205710de, Revision: 00a1
[2026.02.18-14.24.35:446][  0]LogD3D12RHI:   Max supported Feature Level 12_2, shader model 6.7, binding tier 3, wave ops supported, atomic64 supported
[2026.02.18-14.24.35:446][  0]LogD3D12RHI:   Adapter has 32101MB of dedicated video memory, 0MB of dedicated system memory, and 65076MB of shared system memory, 3 output[s]
[2026.02.18-14.24.35:446][  0]LogD3D12RHI:   Driver Version: 581.57 (internal:32.0.15.8157, unified:581.57)
[2026.02.18-14.24.35:446][  0]LogD3D12RHI:      Driver Date: 10-9-2025
[2026.02.18-14.24.35:538][  0]LogD3D12RHI: Found D3D12 adapter 1: AMD Radeon(TM) Graphics (VendorId: 1002, DeviceId: 164e, SubSysId: 7d671462, Revision: 00c1
[2026.02.18-14.24.35:538][  0]LogD3D12RHI:   Max supported Feature Level 12_1, shader model 6.7, binding tier 3, wave ops supported, atomic64 supported
[2026.02.18-14.24.35:538][  0]LogD3D12RHI:   Adapter has 485MB of dedicated video memory, 0MB of dedicated system memory, and 65076MB of shared system memory, 0 output[s]
[2026.02.18-14.24.35:538][  0]LogD3D12RHI:   Driver Version: AMD Software: Adrenalin Edition 26.1.1 (internal:32.0.21041.1000, unified:32.0.21041.1000)
[2026.02.18-14.24.35:538][  0]LogD3D12RHI:      Driver Date: 1-8-2026
[2026.02.18-14.24.35:550][  0]LogD3D12RHI: Found D3D12 adapter 2: Microsoft Basic Render Driver (VendorId: 1414, DeviceId: 008c, SubSysId: 0000, Revision: 0000
[2026.02.18-14.24.35:550][  0]LogD3D12RHI:   Max supported Feature Level 12_1, shader model 6.7, binding tier 3, wave ops supported, atomic64 supported
[2026.02.18-14.24.35:550][  0]LogD3D12RHI:   Adapter has 0MB of dedicated video memory, 0MB of dedicated system memory, and 65076MB of shared system memory, 0 output[s]
[2026.02.18-14.24.35:710][  0]LogD3D12RHI: Found D3D12 adapter 3: NVIDIA GeForce RTX 5090 (VendorId: 10de, DeviceId: 2b85, SubSysId: 205710de, Revision: 00a1
[2026.02.18-14.24.35:710][  0]LogD3D12RHI:   Max supported Feature Level 12_2, shader model 6.7, binding tier 3, wave ops supported, atomic64 supported
[2026.02.18-14.24.35:710][  0]LogD3D12RHI:   Adapter has 32101MB of dedicated video memory, 0MB of dedicated system memory, and 65076MB of shared system memory, 0 output[s]
[2026.02.18-14.24.35:710][  0]LogD3D12RHI:   Driver Version: 581.57 (internal:32.0.15.8157, unified:581.57)
[2026.02.18-14.24.35:710][  0]LogD3D12RHI:      Driver Date: 10-9-2025
[2026.02.18-14.24.35:710][  0]LogD3D12RHI: DirectX Agility SDK runtime found.
[2026.02.18-14.24.35:710][  0]LogD3D12RHI: Chosen D3D12 Adapter Id = 0
    '''

    '''
    When launched with python:

[2026.02.18-14.44.32:914][  0]LogD3D12RHI: Aftermath initialized
[2026.02.18-14.44.32:914][  0]LogD3D12RHI: Loading WinPixEventRuntime.dll for PIX profiling (from ../../../Engine/Binaries/ThirdParty/Windows/WinPixEventRuntime/x64).
[2026.02.18-14.44.32:914][  0]LogRHI: Checking if RHI D3D12 with Feature Level SM6 is supported by your system.
[2026.02.18-14.44.32:953][  0]LogD3D12RHI: D3D12CreateDevice failed with code 0x887A0004
[2026.02.18-14.44.33:078][  0]LogD3D12RHI: Found D3D12 adapter 1: AMD Radeon(TM) Graphics (VendorId: 1002, DeviceId: 164e, SubSysId: 7d671462, Revision: 00c1
[2026.02.18-14.44.33:078][  0]LogD3D12RHI:   Max supported Feature Level 12_1, shader model 6.7, binding tier 3, wave ops supported, atomic64 supported
[2026.02.18-14.44.33:078][  0]LogD3D12RHI:   Adapter has 485MB of dedicated video memory, 0MB of dedicated system memory, and 65076MB of shared system memory, 0 output[s]
[2026.02.18-14.44.33:079][  0]LogD3D12RHI:   Driver Version: AMD Software: Adrenalin Edition 26.1.1 (internal:32.0.21041.1000, unified:32.0.21041.1000)
[2026.02.18-14.44.33:079][  0]LogD3D12RHI:      Driver Date: 1-8-2026
[2026.02.18-14.44.33:085][  0]LogD3D12RHI: Found D3D12 adapter 2: Microsoft Basic Render Driver (VendorId: 1414, DeviceId: 008c, SubSysId: 0000, Revision: 0000
[2026.02.18-14.44.33:085][  0]LogD3D12RHI:   Max supported Feature Level 12_1, shader model 6.7, binding tier 3, wave ops supported, atomic64 supported
[2026.02.18-14.44.33:085][  0]LogD3D12RHI:   Adapter has 0MB of dedicated video memory, 0MB of dedicated system memory, and 65076MB of shared system memory, 0 output[s]
[2026.02.18-14.44.33:112][  0]LogD3D12RHI: D3D12CreateDevice failed with code 0x887A0004
[2026.02.18-14.44.33:112][  0]LogD3D12RHI: DirectX Agility SDK runtime found.
[2026.02.18-14.44.33:112][  0]LogD3D12RHI: Chosen D3D12 Adapter Id = 1
    '''

