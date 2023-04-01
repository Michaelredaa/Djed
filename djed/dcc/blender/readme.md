**Initialize**
- copy `djed/dcc/blender/hooks/djed_startup.py` to `Blender <VERSION>\<VERSION>\scripts\startup`
```
// https://blender.stackexchange.com/questions/158874/changing-startup-file-location
SET BLENDER_USER_CONFIG=%~dp0Portable_Data\Config
SET BLENDER_USER_SCRIPTS=%~dp0Portable_Data\Scripts
    
if not exist %BLENDER_USER_CONFIG% mkdir %BLENDER_USER_CONFIG%
if not exist %BLENDER_USER_SCRIPTS% mkdir %BLENDER_USER_SCRIPTS%
    
start Blender.exe
```