#!/bin/bash
# ============================================================
# Wokwi CLI for Linux/macOS
# ============================================================
# Cross-platform version of wokwi.cmd for Unix systems

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VERSION="2.0"
BUILD_DATE="2025-09-26"

# Colors for Unix terminals
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}============================================================${NC}"
echo -e "${BLUE}🚀 Wokwi CLI v${VERSION} - Universal Toolkit${NC}"
echo -e "${CYAN}============================================================${NC}"

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found in PATH${NC}"
    echo -e "${YELLOW}Please install Python or add it to PATH${NC}"
    echo
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Process arguments
case "$1" in
    "-setup"|"--setup"|"-scan"|"--scan"|"-config"|"--config")
        echo -e "${BLUE}🔍 Running Firmware Scanner...${NC}"
        echo
        $PYTHON_CMD "$SCRIPT_DIR/setup.py"
        if [ $? -eq 0 ]; then
            echo
            echo -e "${GREEN}✅ Setup completed successfully!${NC}"
        else
            echo
            echo -e "${RED}❌ Setup failed${NC}"
            exit 1
        fi
        ;;
    "-diagram"|"--diagram")
        echo -e "${BLUE}📦 Running Diagram Downloader...${NC}"
        echo
        $PYTHON_CMD "$SCRIPT_DIR/diagram.py"
        if [ $? -eq 0 ]; then
            echo
            echo -e "${GREEN}✅ Diagram download completed successfully!${NC}"
        else
            echo
            echo -e "${RED}❌ Diagram download failed${NC}"
            exit 1
        fi
        ;;
    "-version"|"--version"|"-v")
        echo -e "${CYAN}📋 Wokwi CLI Version Information${NC}"
        echo
        echo -e "  ${YELLOW}Version:${NC}        $VERSION"
        echo -e "  ${YELLOW}Build Date:${NC}     $BUILD_DATE"
        echo -e "  ${YELLOW}Python:${NC}         $(${PYTHON_CMD} --version 2>&1)"
        echo -e "  ${YELLOW}Platform:${NC}       $(uname -s) (Bash)"
        echo
        echo -e "${CYAN}🔧 Components:${NC}"
        echo -e "  ${GREEN}✓${NC} Universal Firmware Scanner"
        echo -e "  ${GREEN}✓${NC} Wokwi Diagram Downloader"
        echo -e "  ${GREEN}✓${NC} STM32 + ESP32 Support"
        echo -e "  ${GREEN}✓${NC} Auto Project Detection"
        echo
        ;;
    "-help"|"--help"|"-h"|"")
        echo -e "${YELLOW}📖 WOKWI CLI - Usage Guide${NC}"
        echo
        echo -e "${CYAN}🔧 Setup Commands:${NC}"
        echo -e "  ${GREEN}./wokwi.sh -setup${NC}     Auto scan firmware and create wokwi.toml"
        echo -e "  ${GREEN}./wokwi.sh -scan${NC}      Alias for -setup"
        echo -e "  ${GREEN}./wokwi.sh -config${NC}    Alias for -setup"
        echo
        echo -e "${CYAN}📦 Diagram Commands:${NC}"
        echo -e "  ${GREEN}./wokwi.sh -diagram${NC}   Download diagram.json from Wokwi project"
        echo
        echo -e "${CYAN}ℹ️  Info Commands:${NC}"
        echo -e "  ${GREEN}./wokwi.sh -help${NC}      Show this help"
        echo -e "  ${GREEN}./wokwi.sh -version${NC}   Show version information"
        echo
        echo -e "${CYAN}📁 Supported Projects:${NC}"
        echo -e "  ${YELLOW}• STM32CubeIDE${NC}   (.ioc files, Debug folder)"
        echo -e "  ${YELLOW}• PlatformIO${NC}     (platformio.ini, .pio/build folder)"
        echo -e "  ${YELLOW}• ESP32/Arduino${NC}  (with PlatformIO)"
        echo
        echo -e "${CYAN}🛠️  Examples:${NC}"
        echo -e "  ${GREEN}./wokwi.sh -setup${NC}     # Scan and setup firmware"
        echo -e "  ${GREEN}./wokwi.sh -diagram${NC}   # Download diagram from URL"
        echo
        ;;
    *)
        echo -e "${RED}❌ Invalid command: $1${NC}"
        echo
        $0 -help
        exit 1
        ;;
esac

echo
echo -e "${CYAN}Thanks for using Wokwi CLI! 🚀${NC}"