@echo off
REM ============================================================
REM Wokwi Command Line Interface (CLI)
REM ============================================================
REM Công cụ tổng hợp để quản lý Wokwi projects
REM 
REM Cách sử dụng:
REM   wokwi.cmd -setup          : Tự động scan và setup firmware
REM   wokwi.cmd -diagram        : Download diagram.json từ Wokwi
REM   wokwi.cmd -help           : Hiển thị hướng dẫn
REM   wokwi.cmd -version        : Hiển thị phiên bản
REM ============================================================

setlocal EnableDelayedExpansion

REM Lấy đường dẫn của script hiện tại
set SCRIPT_DIR=%~dp0

REM Colors for Windows (limited support)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "RESET=[0m"

REM Thông tin phiên bản
set VERSION=2.0
set BUILD_DATE=2025-09-26

REM Banner
echo ============================================================
echo   Wokwi CLI v%VERSION% - Universal Toolkit
echo ============================================================

REM Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python khong duoc tim thay trong PATH
    echo [INFO] Vui long cai dat Python hoac them vao PATH
    echo.
    goto :show_help
)

REM Xử lý arguments
if "%1"=="" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="--help" goto :show_help
if "%1"=="-help" goto :show_help

if "%1"=="-v" goto :show_version
if "%1"=="--version" goto :show_version
if "%1"=="-version" goto :show_version

if "%1"=="-setup" goto :run_setup
if "%1"=="--setup" goto :run_setup

if "%1"=="-diagram" goto :run_diagram
if "%1"=="--diagram" goto :run_diagram

if "%1"=="-scan" goto :run_setup
if "%1"=="--scan" goto :run_setup

if "%1"=="-config" goto :run_setup
if "%1"=="--config" goto :run_setup

REM Command khong hop le
echo [ERROR] Command khong hop le: %1
echo.
goto :show_help

REM ============================================================
REM Functions
REM ============================================================

:show_help
echo WOKWI CLI - Huong dan su dung
echo.
echo Setup Commands:
echo   wokwi -setup       Tu dong scan firmware va tao wokwi.toml
echo   wokwi -scan        Alias cho -setup
echo   wokwi -config      Alias cho -setup
echo.
echo Diagram Commands:
echo   wokwi -diagram     Download diagram.json tu Wokwi project
echo.
echo Info Commands:
echo   wokwi -help        Hien thi huong dan nay
echo   wokwi -version     Hien thi thong tin phien ban
echo.
echo Supported Projects:
echo   * STM32CubeIDE     (.ioc files, Debug folder)
echo   * PlatformIO       (platformio.ini, .pio/build folder)  
echo   * ESP32/Arduino    (voi PlatformIO)
echo.
echo Examples:
echo   wokwi -setup       # Scan va setup firmware
echo   wokwi -diagram     # Download diagram tu URL
echo.
goto :end

:show_version
echo Wokwi CLI Version Information
echo.
echo   Version:        %VERSION%
echo   Build Date:     %BUILD_DATE%
echo   Python:         
python --version 2>nul
echo   Platform:       Windows (CMD/PowerShell)
echo.
echo Components:
echo   [OK] Universal Firmware Scanner
echo   [OK] Wokwi Diagram Downloader  
echo   [OK] STM32 + ESP32 Support
echo   [OK] Auto Project Detection
echo.
goto :end

:run_setup
echo [INFO] Running Firmware Scanner...
echo.
python "%SCRIPT_DIR%setup.py"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Setup failed with error code %errorlevel%
    goto :end
)
echo.
echo [SUCCESS] Setup completed successfully!
goto :end

:run_diagram
echo [INFO] Running Diagram Downloader...
echo.
python "%SCRIPT_DIR%diagram.py"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Diagram download failed with error code %errorlevel%
    goto :end
)
echo.
echo [SUCCESS] Diagram download completed successfully!
goto :end

:end
echo.
echo Thanks for using Wokwi CLI!
exit /b 0