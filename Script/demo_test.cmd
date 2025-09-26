@echo off
REM ============================================================
REM Wokwi CLI Executable - Full Feature Demo
REM ============================================================

echo ============================================================
echo   Wokwi CLI Executable - Demo Test Suite
echo ============================================================
echo.

echo [INFO] Testing all wokwi.exe commands...
echo.

echo 1. VERSION TEST:
echo ----------------------------------------
wokwi.exe version
echo.

echo 2. HELP TEST:
echo ----------------------------------------
wokwi.exe help
echo.

echo 3. DIAGRAM TEST (with file input):
echo ----------------------------------------
if exist test_url.txt (
    wokwi.exe diagram test_url.txt
    echo.
    if exist diagram.json (
        echo [SUCCESS] diagram.json created successfully!
        echo File size:
        dir diagram.json | findstr diagram.json
    ) else (
        echo [ERROR] diagram.json not found
    )
) else (
    echo [ERROR] test_url.txt not found
)
echo.

echo 4. SETUP TEST (if in project directory):
echo ----------------------------------------
wokwi.exe setup
echo.

echo ============================================================
echo   Demo completed!
echo ============================================================
echo.

echo Generated files:
dir /b *.json *.toml 2>nul
echo.

echo [INFO] wokwi.exe size: 
dir wokwi.exe | findstr wokwi.exe
echo.

pause