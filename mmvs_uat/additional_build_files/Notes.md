# ...
Additional Build Files are copied only for specific build using a json config file.

Example:
```json
{
    "Server_Win64_DebugGame": ["MyFolder01", "MyFolder02", "MyFolder03"],
    "Server_Win64_Development": [],
    "Server_Win64_Shipping": [],
    "Server_Linux_DebugGame": [],
    "Server_Linux_Development": [],
    "Server_Linux_Shipping": [],
    "Server_LinuxArm64_DebugGame": [],
    "Server_LinuxArm64_Development": [],
    "Server_LinuxArm64_Shipping": [],
    "Client_Win64_DebugGame": [],
    "Client_Win64_Development": [],
    "Client_Win64_Shipping": [],
    "Client_Linux_DebugGame": [],
    "Client_Linux_Development": [],
    "Client_Linux_Shipping": [],
    "Client_LinuxArm64_DebugGame": [],
    "Client_LinuxArm64_Development": [],
    "Client_LinuxArm64_Shipping": []
}
```