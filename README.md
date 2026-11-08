# Unreal-Build-Game

An automated build tool for Unreal Engine projects. It lets you configure and run client and server builds for different platforms and build modes, then organizes the output and creates ZIP packages.

> **Note:** The build settings and project paths are currently hardcoded and configured for development of the [MMVS video game](https://github.com/xavier150/MMVS). A command-line interface using a JSON configuration file is planned for a future update.

![MMVS UAT build configuration menu](https://github.com/xavier150/Unreal-Build-Game/wiki/images/mmvs-uat-menu.png)


Example Windows folder:

```text
F:\MMVS_GameBuilds\
├── DebugGame\
│   ├── Windows\
│   │   ├── MacroMicroVrService.exe
│   │   └── ...
│   ├── WindowsServer\
│   │   ├── MMVS_Server.exe
│   │   └── ...
│   └── MMVS - <version> - Win64.zip
├── Development\
│   ├── Windows\
│   │   └── ...
│   ├── WindowsServer\
│   │   └── ...
│   └── MMVS - <version> - Win64.zip
├── Shipping\
│   ├── Windows\
│   │   └── ...
│   ├── WindowsServer\
│   │   └── ...
│   └── MMVS - <version> - Win64.zip
└── UAT_LOGS\
    └── ...
```

![Exported build files](https://github.com/xavier150/Unreal-Build-Game/wiki/images/exported-build-files.png)

## Additional Notes

You can join my Discord server for more information or if you need help.  

Discord [<img src="https://github.com/xavier150/Unreal-Build-Game/wiki/images/socials/discord_symbol_blurple.png" alt="Discord Icon" width="auto" height="12">](https://discord.gg/XuYeGCFtxa) ->
[BleuRaven side projects](https://discord.gg/XuYeGCFtxa)  