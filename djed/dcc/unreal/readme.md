How to activate Djed on unreal 5

- Plugins >> Scripting >> Python -AllowPythonDeveloperMode
- Plugins >> Scripting >> Editor scripting utility
- Plugins >> Scripting >> sequencer scripting

- Project Settings >> python >> Enable Remote Execution -AllowRemoteExecution
- Project Settings >> python >> Developer Mode -AllowPythonDeveloperMode






**TODO**
- creates generic master material
- manage the switch between virtual textures and non-virtual
- manage colorspace
- automate the initial settings



**To Stop Port**
-  `netstat -ano | findstr :PORT_NUMBER`
-   `taskkill /PID PROCESS_PID /F`
- or using `os.kill(PROCESS_PID, 9)`