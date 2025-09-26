#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wokwi CLI - Standalone Executable Version
==========================================
Self-contained executable with all embedded functionality
"""

import sys
import os
import argparse
import requests
import zipfile
import tempfile
import json
import glob
import configparser
import time
from pathlib import Path

# Colors for output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_banner():
    """Print Wokwi CLI banner"""
    print("=" * 60)
    print("🚀 Wokwi CLI v2.0 - Universal Toolkit (Standalone)")
    print("=" * 60)

def print_version():
    """Print version information"""
    print(f"{Colors.CYAN}📋 Wokwi CLI Version Information{Colors.RESET}")
    print()
    print(f"  {Colors.YELLOW}Version:{Colors.RESET}        2.0 (Standalone)")
    print(f"  {Colors.YELLOW}Build Date:{Colors.RESET}     2025-09-26")
    print(f"  {Colors.YELLOW}Python:{Colors.RESET}         {sys.version.split()[0]}")
    print(f"  {Colors.YELLOW}Platform:{Colors.RESET}       {os.name} ({sys.platform})")
    print()
    print(f"{Colors.CYAN}🔧 Components:{Colors.RESET}")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Universal Firmware Scanner")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Wokwi Diagram Downloader")
    print(f"  {Colors.GREEN}✓{Colors.RESET} STM32 + ESP32 Support")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Auto Project Detection")
    print(f"  {Colors.GREEN}✓{Colors.RESET} File Input Support")

def print_help():
    """Print help information"""
    print(f"{Colors.YELLOW}📖 WOKWI CLI - Usage Guide{Colors.RESET}")
    print()
    print(f"{Colors.CYAN}🔧 Setup Commands:{Colors.RESET}")
    print(f"  {Colors.GREEN}wokwi setup{Colors.RESET}                Auto scan firmware and create wokwi.toml")
    print(f"  {Colors.GREEN}wokwi scan{Colors.RESET}                 Alias for setup")
    print(f"  {Colors.GREEN}wokwi config{Colors.RESET}               Alias for setup")
    print()
    print(f"{Colors.CYAN}📦 Diagram Commands:{Colors.RESET}")
    print(f"  {Colors.GREEN}wokwi diagram{Colors.RESET}              Download diagram from url.txt")
    print(f"  {Colors.GREEN}wokwi diagram <file>{Colors.RESET}       Download diagram from specific file")
    print(f"  {Colors.GREEN}wokwi diagram <url>{Colors.RESET}        Download diagram from URL directly")
    print()
    print(f"{Colors.CYAN}ℹ️  Info Commands:{Colors.RESET}")
    print(f"  {Colors.GREEN}wokwi help{Colors.RESET}                 Show this help")
    print(f"  {Colors.GREEN}wokwi version{Colors.RESET}              Show version information")
    print()
    print(f"{Colors.CYAN}📁 Supported Projects:{Colors.RESET}")
    print(f"  {Colors.YELLOW}• STM32CubeIDE{Colors.RESET}   (.ioc files, Debug folder)")
    print(f"  {Colors.YELLOW}• PlatformIO{Colors.RESET}     (platformio.ini, .pio/build folder)")
    print(f"  {Colors.YELLOW}• ESP32/Arduino{Colors.RESET}  (with PlatformIO)")
    print()
    print(f"{Colors.CYAN}🛠️  Examples:{Colors.RESET}")
    print(f"  {Colors.GREEN}wokwi setup{Colors.RESET}                # Scan and setup firmware")
    print(f"  {Colors.GREEN}wokwi diagram{Colors.RESET}              # Download from url.txt")
    print(f"  {Colors.GREEN}wokwi diagram ./url.txt{Colors.RESET}    # Download from specific file")
    print(f"  {Colors.GREEN}wokwi diagram https://wokwi.com/...{Colors.RESET}  # Direct URL")

# ============================================================
# FIRMWARE SCANNER MODULE (Embedded)
# ============================================================

def scan_for_firmware_files(search_root=None):
    """Automatically scan for .bin and .elf files"""
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
    """Find project root directory"""
    current_dir = Path.cwd()
    
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
        base_name = file_path.stem
        dir_path = file_path.parent
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
    """Allow user to select firmware group or automatically select"""
    if not firmware_groups:
        return None
    
    if len(firmware_groups) == 1:
        key = list(firmware_groups.keys())[0]
        return firmware_groups[key]
    
    # Multiple groups, display menu
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

def run_setup():
    """Run firmware setup"""
    print(f"{Colors.BLUE}🔍 Running Firmware Scanner...{Colors.RESET}")
    print()
    
    try:
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
            return 1
        
        print(f"✓ Found {Colors.GREEN}{len(firmware_files)}{Colors.RESET} firmware files")
        
        # Group files by .bin/.elf pairs
        firmware_groups = group_firmware_files(firmware_files)
        
        if not firmware_groups:
            print(f"{Colors.RED}❌ No complete .bin/.elf pairs found{Colors.RESET}")
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
        
        print(f"\n{Colors.GREEN}🎉 Complete!{Colors.RESET}")
        return 0
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
        return 1

# ============================================================
# DIAGRAM DOWNLOADER MODULE (Embedded)
# ============================================================

def read_url_from_source(input_source):
    """Read URL from source (file or direct URL)"""
    if input_source.startswith('http'):
        return input_source
    
    # Read from file
    input_path = Path(input_source)
    if not input_path.is_absolute():
        input_path = Path.cwd() / input_path
    
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")
    
    with open(input_path, "r", encoding="utf-8") as f:
        url = f.read().strip()
    
    # Process URL
    if url.startswith("https://wokwi.com/projects/"):
        return url
    elif url.isdigit():
        return f"https://wokwi.com/projects/{url}"
    else:
        return url

def download_and_extract_diagram(wokwi_url):
    """Download ZIP from Wokwi and extract diagram.json"""
    try:
        # Create download URL
        if "/projects/" in wokwi_url:
            project_id = wokwi_url.split("/projects/")[1].split("/")[0]
            download_url = f"https://wokwi.com/api/projects/{project_id}/zip"
        else:
            print(f"{Colors.RED}❌ Invalid URL: {wokwi_url}{Colors.RESET}")
            return False
        
        print(f"🌐 Downloading from: {Colors.CYAN}{download_url}{Colors.RESET}")
        
        # Download ZIP file
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        # Extract diagram.json
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                if 'diagram.json' in zip_ref.namelist():
                    zip_ref.extract('diagram.json', '.')
                    print(f"{Colors.GREEN}✅ Downloaded diagram.json successfully!{Colors.RESET}")
                    
                    # Display information
                    with open('diagram.json', 'r', encoding='utf-8') as f:
                        diagram_data = json.load(f)
                        print(f"📊 Diagram info:")
                        print(f"  - Version: {diagram_data.get('version', 'N/A')}")
                        print(f"  - Parts: {len(diagram_data.get('parts', []))}")
                        print(f"  - Connections: {len(diagram_data.get('connections', []))}")
                    
                    return True
                else:
                    print(f"{Colors.RED}❌ diagram.json not found in ZIP{Colors.RESET}")
                    return False
        finally:
            os.unlink(temp_file_path)
            
    except requests.RequestException as e:
        print(f"{Colors.RED}❌ Download error: {e}{Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
        return False

def run_diagram(input_source=None):
    """Run diagram downloader"""
    print(f"{Colors.BLUE}📦 Running Diagram Downloader...{Colors.RESET}")
    print()
    
    try:
        # Process input source
        if input_source:
            if input_source.startswith('http'):
                print(f"🌐 Using direct URL: {input_source}")
                url = input_source
            else:
                print(f"📁 Using input file: {input_source}")
                url = read_url_from_source(input_source)
        else:
            # Default to using url.txt
            default_url_file = Path.cwd() / "url.txt"
            if default_url_file.exists():
                print(f"📁 Using default file: {default_url_file}")
                url = read_url_from_source(str(default_url_file))
            else:
                print(f"{Colors.YELLOW}⚠ No url.txt found in current directory{Colors.RESET}")
                print(f"{Colors.CYAN}Usage: wokwi diagram <file_or_url>{Colors.RESET}")
                return 1
        
        print(f"🎯 Target URL: {Colors.CYAN}{url}{Colors.RESET}")
        print()
        
        # Download diagram
        if download_and_extract_diagram(url):
            print(f"\n{Colors.GREEN}✅ Diagram download completed successfully!{Colors.RESET}")
            return 0
        else:
            print(f"\n{Colors.RED}❌ Diagram download failed{Colors.RESET}")
            return 1
            
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
        return 1

# ============================================================
# MAIN CLI
# ============================================================

def main():
    """Main CLI entry point"""
    print_banner()
    
    if len(sys.argv) < 2:
        print_help()
        return 0
    
    command = sys.argv[1].lower()
    
    # Setup commands
    if command in ['setup', 'scan', 'config']:
        return run_setup()
    
    # Diagram commands
    elif command == 'diagram':
        input_source = sys.argv[2] if len(sys.argv) > 2 else None
        return run_diagram(input_source)
    
    # Info commands
    elif command in ['help', 'h', '--help', '-help']:
        print_help()
        return 0
    
    elif command in ['version', 'v', '--version', '-version']:
        print_version()
        return 0
    
    else:
        print(f"{Colors.RED}❌ Unknown command: {command}{Colors.RESET}")
        print()
        print_help()
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠ Operation cancelled by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)