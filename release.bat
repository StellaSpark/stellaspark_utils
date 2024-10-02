@echo off
REM Check if the argument is passed
if "%~1"=="" (
    echo Usage: release.bat version
    exit /b 1
)

REM Execute the upload.sh script via bash (ensure bash is in your PATH)
bash -c "./release.sh %~1"

REM Pause the command window to view output before closing
pause