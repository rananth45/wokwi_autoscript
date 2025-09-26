#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wokwi CLI - Executable Version
==============================
Command Line Interface for Wokwi Simulator
Supports file inputs and all original features
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))

# Import modules
try:
    from setup import main as setup_main
    from diagram import main as diagram_main
except ImportError:
    # Fallback if import fails
    setup_main = None
    diagram_main = None

# Colors for output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    
    @classmethod
    def disable_on_windows(cls):
        """Disable colors on Windows CMD (optional)"""
        if os.name == 'nt':
            cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = cls.CYAN = cls.RESET = ''

def print_banner():
    """Print Wokwi CLI banner"""
    print("=" * 60)
    print("🚀 Wokwi CLI v2.0 - Universal Toolkit (Executable)")
    print("=" * 60)

def print_version():
    """Print version information"""
    print(f"{Colors.CYAN}📋 Wokwi CLI Version Information{Colors.RESET}")
    print()
    print(f"  {Colors.YELLOW}Version:{Colors.RESET}        2.0")
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

def run_setup():
    """Run firmware setup"""
    print(f"{Colors.BLUE}🔍 Running Firmware Scanner...{Colors.RESET}")
    print()
    
    if setup_main:
        try:
            result = setup_main()
            if result == 0:
                print()
                print(f"{Colors.GREEN}✅ Setup completed successfully!{Colors.RESET}")
                return 0
            else:
                print()
                print(f"{Colors.RED}❌ Setup failed with error code {result}{Colors.RESET}")
                return result
        except Exception as e:
            print()
            print(f"{Colors.RED}❌ Setup failed: {e}{Colors.RESET}")
            return 1
    else:
        # Fallback to subprocess
        script_path = current_dir.parent / "setup.py"
        try:
            result = subprocess.run([sys.executable, str(script_path)], 
                                  capture_output=False, text=True)
            return result.returncode
        except Exception as e:
            print(f"{Colors.RED}❌ Could not run setup: {e}{Colors.RESET}")
            return 1

def run_diagram(input_source=None):
    """Run diagram downloader with optional input source"""
    print(f"{Colors.BLUE}📦 Running Diagram Downloader...{Colors.RESET}")
    print()
    
    # Process input source
    if input_source:
        if input_source.startswith('http'):
            # Direct URL
            print(f"🌐 Using direct URL: {input_source}")
            # Create temporary file with URL
            temp_file = current_dir / "temp_url.txt"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(input_source)
            
            # Set environment variable so diagram.py knows which file to read
            os.environ['WOKWI_URL_FILE'] = str(temp_file)
        else:
            # File path
            input_path = Path(input_source)
            if not input_path.is_absolute():
                input_path = Path.cwd() / input_path
            
            if not input_path.exists():
                print(f"{Colors.RED}❌ File not found: {input_path}{Colors.RESET}")
                return 1
            
            print(f"📁 Using input file: {input_path}")
            os.environ['WOKWI_URL_FILE'] = str(input_path)
    else:
        # Default to using url.txt in current directory
        default_url_file = Path.cwd() / "url.txt"
        if default_url_file.exists():
            print(f"📁 Using default file: {default_url_file}")
            os.environ['WOKWI_URL_FILE'] = str(default_url_file)
        else:
            print(f"{Colors.YELLOW}⚠ No url.txt found in current directory{Colors.RESET}")
            print(f"{Colors.CYAN}Usage: wokwi diagram <file_or_url>{Colors.RESET}")
            return 1
    
    try:
        if diagram_main:
            try:
                result = diagram_main()
                if result == 0:
                    print()
                    print(f"{Colors.GREEN}✅ Diagram download completed successfully!{Colors.RESET}")
                    return 0
                else:
                    print()
                    print(f"{Colors.RED}❌ Diagram download failed with error code {result}{Colors.RESET}")
                    return result
            except Exception as e:
                print()
                print(f"{Colors.RED}❌ Diagram download failed: {e}{Colors.RESET}")
                return 1
        else:
            # Fallback to subprocess
            script_path = current_dir.parent / "diagram.py"
            try:
                result = subprocess.run([sys.executable, str(script_path)], 
                                      capture_output=False, text=True)
                return result.returncode
            except Exception as e:
                print(f"{Colors.RED}❌ Could not run diagram downloader: {e}{Colors.RESET}")
                return 1
    finally:
        # Clean up environment
        if 'WOKWI_URL_FILE' in os.environ:
            del os.environ['WOKWI_URL_FILE']
        
        # Clean up temp file
        temp_file = current_dir / "temp_url.txt"
        if temp_file.exists():
            temp_file.unlink()

def main():
    """Main CLI entry point"""
    # Disable colors on Windows if needed (uncomment next line if colors cause issues)
    # Colors.disable_on_windows()
    
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