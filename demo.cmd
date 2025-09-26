@echo off
REM ============================================================
REM Wokwi CLI Demo Script
REM ============================================================
REM Demonstrates all Wokwi CLI features

echo ============================================================
echo   Wokwi CLI Demo - All Features
echo ============================================================
echo.

echo [DEMO] Testing all CLI commands...
echo.

echo 1. Version Information:
echo ----------------------------------------
call wokwi.cmd -version
echo.

echo 2. Help Information:
echo ----------------------------------------  
call wokwi.cmd -help
echo.

echo 3. Firmware Setup (with shorthand):
echo ----------------------------------------
call w.cmd -setup
echo.

echo ============================================================
echo   Demo completed! 
echo ============================================================
echo.
echo Available files in current directory:
dir /b *.toml *.json *.py *.cmd *.sh 2>nul
echo.
pause