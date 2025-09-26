#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Script for Wokwi CLI Executable
====================================
Creates wokwi.exe using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("📦 Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install PyInstaller")
        return False

def build_executable():
    """Build executable with PyInstaller"""
    print("🔨 Building Wokwi CLI executable...")
    
    # Paths
    script_dir = Path(__file__).parent
    main_script = script_dir / "wokwi_standalone.py"
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single executable file
        "--console",                    # Console application
        "--name=wokwi",                # Output name
        "--distpath=.",                # Output directory
        "--workpath=./build",          # Build directory
        "--specpath=./build",          # Spec file directory
        "--clean",                     # Clean cache
        str(main_script)
    ]
    
    try:
        # Change to script directory
        old_cwd = os.getcwd()
        os.chdir(script_dir)
        
        # Run PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            
            # Check if executable exists
            exe_path = script_dir / "wokwi.exe"
            if exe_path.exists():
                print(f"📁 Executable created: {exe_path}")
                print(f"📊 Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
                return True
            else:
                print("❌ Executable not found after build")
                return False
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False
    finally:
        os.chdir(old_cwd)

def create_test_files():
    """Create test files for executable"""
    script_dir = Path(__file__).parent
    
    # Test URL file
    test_url = script_dir / "test_url.txt"
    test_url.write_text("https://wokwi.com/projects/442394281549660161\n")
    
    # Test batch file
    test_batch = script_dir / "test_wokwi.cmd"
    test_batch.write_text("""@echo off
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
""")
    
    print(f"📝 Created test files:")
    print(f"  - {test_url}")
    print(f"  - {test_batch}")

def main():
    print("=" * 60)
    print("🔧 Wokwi CLI Executable Builder")
    print("=" * 60)
    print()
    
    # Check PyInstaller
    if not check_pyinstaller():
        print("⚠ PyInstaller not found")
        if input("Install PyInstaller? (y/n): ").lower() == 'y':
            if not install_pyinstaller():
                return 1
        else:
            print("❌ PyInstaller required for building")
            return 1
    
    print("✅ PyInstaller found")
    print()
    
    # Build executable
    if build_executable():
        print()
        print("🎉 Build completed successfully!")
        print()
        
        # Create test files
        create_test_files()
        print()
        
        print("🚀 Usage:")
        print("  wokwi.exe setup              # Firmware scanning")
        print("  wokwi.exe diagram            # Download from url.txt")
        print("  wokwi.exe diagram ./url.txt  # Download from specific file")
        print("  wokwi.exe help               # Show help")
        print()
        print("📁 Test with: test_wokwi.cmd")
        
        return 0
    else:
        print("❌ Build failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())