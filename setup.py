#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wokwi Setup - Universal Firmware Scanner
========================================
Script to automatically update wokwi.toml in current directory
Auto scan .bin and .elf files for both STM32 and ESP32
Supports:
- STM32CubeIDE projects (Debug folder)
- PlatformIO projects (.pio/build folder)
"""

import os
import glob
import configparser
from pathlib import Path
import time

# ANSI color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def scan_for_firmware_files(search_root=None):
    """
    Auto scan for .bin and .elf files
    Search in:
    1. STM32 Debug folders
    2. PlatformIO build folders
    """
    if search_root is None:
        search_root = Path.cwd()
    else:
        search_root = Path(search_root)
    
    firmware_files = []
    
    # 1. Scan STM32 Debug folders
    print(f"🔍 Scanning STM32 Debug folders...")
    debug_patterns = [
        "**/Debug/**/*.bin",
        "**/Debug/**/*.elf",
        "**/build/**/*.bin", 
        "**/build/**/*.elf"
    ]
    
    for pattern in debug_patterns:
        for file_path in search_root.rglob(pattern):
            if file_path.is_file():
                firmware_files.append(file_path)
    
    # 2. Scan PlatformIO build folders
    print(f"🔍 Scanning PlatformIO build folders...")
    pio_patterns = [
        "**/.pio/build/**/*.bin",
        "**/.pio/build/**/*.elf"
    ]
    
    for pattern in pio_patterns:
        for file_path in search_root.rglob(pattern):
            if file_path.is_file():
                firmware_files.append(file_path)
    
    return firmware_files

def find_project_root():
    """Find project root directory (STM32 or PlatformIO)"""
    current_dir = Path.cwd()
    
    # Search in current directory and parent directories
    for path in [current_dir] + list(current_dir.parents):
        # Check STM32CubeIDE project
        ioc_files = list(path.glob("*.ioc"))
        if ioc_files:
            return path, "STM32"
        
        # Check PlatformIO project
        platformio_ini = path / "platformio.ini"
        if platformio_ini.exists():
            return path, "PlatformIO"
    
    return None, None

def group_firmware_files(firmware_files):
    """Group firmware files by .bin and .elf pairs"""
    file_groups = {}
    
    for file_path in firmware_files:
        # Get filename without extension
        base_name = file_path.stem
        dir_path = file_path.parent
        
        # Create unique key for each group
        group_key = f"{dir_path}/{base_name}"
        
        if group_key not in file_groups:
            file_groups[group_key] = {'bin': None, 'elf': None, 'path': dir_path, 'name': base_name}
        
        if file_path.suffix.lower() == '.bin':
            file_groups[group_key]['bin'] = file_path
        elif file_path.suffix.lower() == '.elf':
            file_groups[group_key]['elf'] = file_path
    
    # Only return groups with both .bin and .elf
    complete_groups = {}
    for key, group in file_groups.items():
        if group['bin'] and group['elf']:
            complete_groups[key] = group
    
    return complete_groups

def select_firmware_group(firmware_groups):
    """Allow user to select firmware group or auto select"""
    if not firmware_groups:
        return None
    
    if len(firmware_groups) == 1:
        # Only 1 group, auto select
        key = list(firmware_groups.keys())[0]
        return firmware_groups[key]
    
    # Multiple groups, show menu
    print(f"\n{Colors.CYAN}Found {len(firmware_groups)} firmware groups:{Colors.RESET}")
    
    groups_list = list(firmware_groups.items())
    for i, (key, group) in enumerate(groups_list, 1):
        print(f"{i}. {Colors.YELLOW}{group['name']}{Colors.RESET} ({group['path']})")
        print(f"   📁 BIN: {group['bin'].name}")
        print(f"   📁 ELF: {group['elf'].name}")
        print()
    
    while True:
        try:
            choice = input(f"Select firmware group (1-{len(groups_list)}) or Enter for latest: ").strip()
            
            if choice == "":
                # Select latest file based on modification time
                latest_group = None
                latest_time = 0
                
                for key, group in firmware_groups.items():
                    bin_time = group['bin'].stat().st_mtime
                    elf_time = group['elf'].stat().st_mtime
                    file_time = max(bin_time, elf_time)
                    
                    if file_time > latest_time:
                        latest_time = file_time
                        latest_group = group
                
                return latest_group
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(groups_list):
                return groups_list[choice_num - 1][1]
            else:
                print(f"{Colors.RED}❌ Please select number from 1 to {len(groups_list)}{Colors.RESET}")
        
        except (ValueError, KeyboardInterrupt):
            print(f"{Colors.RED}❌ Invalid selection{Colors.RESET}")
            return None

def create_relative_path(from_dir, to_file):
    """Create relative path and normalize for Windows"""
    rel_path = os.path.relpath(to_file, from_dir)
    return rel_path.replace('/', '\\')

def update_wokwi_toml(firmware_bin, firmware_elf):
    """Update wokwi.toml file in current directory"""
    current_dir = Path.cwd()
    wokwi_toml = current_dir / "wokwi.toml"
    
    # Create relative paths
    bin_path = create_relative_path(current_dir, firmware_bin)
    elf_path = create_relative_path(current_dir, firmware_elf)
    
    # Get file information
    bin_size = firmware_bin.stat().st_size
    elf_size = firmware_elf.stat().st_size
    bin_time = time.ctime(firmware_bin.stat().st_mtime)
    
    content = f"""# Wokwi Configuration
# Generated by Universal Firmware Scanner
# Firmware: {firmware_bin.name} ({bin_size:,} bytes)
# ELF: {firmware_elf.name} ({elf_size:,} bytes)  
# Build time: {bin_time}

[wokwi]
version = 1
firmware = '{bin_path}'
elf = '{elf_path}'
"""
    
    with open(wokwi_toml, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return wokwi_toml

def main():
    print("=" * 60)
    print("🔧 Wokwi Setup - Universal Firmware Scanner")
    print("=" * 60)
    
    # Find project root
    project_root, project_type = find_project_root()
    if not project_root:
        print(f"{Colors.YELLOW}⚠ Project root not found, scanning from current directory{Colors.RESET}")
        project_root = Path.cwd()
        project_type = "Unknown"
    
    print(f"📂 Project: {Colors.GREEN}{project_root}{Colors.RESET}")
    print(f"🏷  Type: {Colors.CYAN}{project_type}{Colors.RESET}")
    
    # Scan firmware files
    print(f"\n🔍 {Colors.BLUE}Scanning firmware files...{Colors.RESET}")
    firmware_files = scan_for_firmware_files(project_root)
    
    if not firmware_files:
        print(f"{Colors.RED}❌ No .bin or .elf files found{Colors.RESET}")
        print(f"\n{Colors.CYAN}Suggestions:{Colors.RESET}")
        print("• STM32: Build project in STM32CubeIDE")
        print("• ESP32: Run 'pio run' in PlatformIO")
        return 1
    
    print(f"✓ Found {Colors.GREEN}{len(firmware_files)}{Colors.RESET} firmware files")
    
    # Group files by .bin/.elf pairs
    firmware_groups = group_firmware_files(firmware_files)
    
    if not firmware_groups:
        print(f"{Colors.RED}❌ No complete .bin/.elf pairs found{Colors.RESET}")
        print(f"\n{Colors.CYAN}Files found:{Colors.RESET}")
        for file_path in firmware_files:
            print(f"  📁 {file_path}")
        return 1
    
    print(f"✓ Found {Colors.GREEN}{len(firmware_groups)}{Colors.RESET} complete firmware groups")
    
    # Select firmware group
    selected_group = select_firmware_group(firmware_groups)
    if not selected_group:
        print(f"{Colors.RED}❌ No firmware group selected{Colors.RESET}")
        return 1
    
    firmware_bin = selected_group['bin']
    firmware_elf = selected_group['elf']
    
    print(f"\n✓ Selected: {Colors.YELLOW}{selected_group['name']}{Colors.RESET}")
    print(f"  📁 BIN: {firmware_bin}")
    print(f"  📁 ELF: {firmware_elf}")
    
    # Update wokwi.toml
    try:
        wokwi_toml = update_wokwi_toml(firmware_bin, firmware_elf)
        
        print(f"\n{Colors.GREEN}✓ Updated: {wokwi_toml}{Colors.RESET}")
        
        # Display content
        print(f"\n{Colors.CYAN}📄 wokwi.toml content:{Colors.RESET}")
        with open(wokwi_toml, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip().startswith('#'):
                    print(f"{Colors.CYAN}{line_num:2d}: {line.rstrip()}{Colors.RESET}")
                elif '=' in line:
                    print(f"{Colors.YELLOW}{line_num:2d}: {line.rstrip()}{Colors.RESET}")
                else:
                    print(f"{line_num:2d}: {line.rstrip()}")
        
        print(f"\n{Colors.GREEN}🎉 Completed!{Colors.RESET}")
        return 0
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error updating wokwi.toml: {e}{Colors.RESET}")
        return 1

if __name__ == "__main__":
    exit(main())
