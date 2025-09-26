@echo off
REM Universal Firmware Scanner Launcher
REM Tự động tìm và cấu hình firmware cho Wokwi

echo ============================================================
echo 🔧 Wokwi Universal Firmware Scanner
echo ============================================================
echo.

REM Kiểm tra Python có tồn tại không
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python không được tìm thấy trong PATH
    echo Vui lòng cài đặt Python hoặc thêm vào PATH
    pause
    exit /b 1
)

REM Chạy script Python
python "%~dp0setup.py"

echo.
echo Nhấn phím bất kỳ để đóng...
pause >nul