@echo off
echo Testing Wokwi CLI executable...
echo.

echo 1. Version test:
wokwi.exe version
echo.

echo 2. Help test:
wokwi.exe help
echo.

echo 3. Diagram test (if test_url.txt exists):
if exist test_url.txt (
    wokwi.exe diagram test_url.txt
) else (
    echo test_url.txt not found
)
echo.

pause
