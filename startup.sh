#!/bin/bash
echo "============================================================"
echo "🚀 Highrise Music Bot - KingRadio Version Startup"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
echo "📋 Checking Python..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3 not found!${NC}"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

# Check pip
echo "📋 Checking pip..."
if command_exists pip3; then
    echo -e "${GREEN}✅ pip3 found${NC}"
else
    echo -e "${YELLOW}⚠️ pip3 not found, trying pip...${NC}"
    if ! command_exists pip; then
        echo -e "${RED}❌ pip not found!${NC}"
        exit 1
    fi
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt --quiet --upgrade 2>/dev/null || pip install -r requirements.txt --quiet --upgrade

# Check and install yt-dlp
echo ""
echo "📋 Checking yt-dlp..."
if command_exists yt-dlp; then
    echo -e "${GREEN}✅ yt-dlp found${NC}"
else
    echo -e "${YELLOW}⚠️ yt-dlp not found, attempting to install...${NC}"
    pip3 install yt-dlp --quiet
fi

# Check FFmpeg
echo ""
echo "📋 Checking FFmpeg..."
if command_exists ffmpeg; then
    echo -e "${GREEN}✅ ffmpeg found${NC}"
else
    echo -e "${RED}❌ FFmpeg not found!${NC}"
    echo "Please install FFmpeg manually for KingRadio streaming"
    exit 1
fi

# Create necessary directories
echo ""
echo "📁 Creating KingRadio directories..."
mkdir -p song_cache downloads backups
echo -e "${GREEN}✅ Directories ready${NC}"

# Check environment variables
echo ""
echo "🔐 Checking environment variables..."
MISSING_VARS=0

if [ -z "$HIGHRISE_BOT_TOKEN" ]; then
    echo -e "${YELLOW}⚠️ HIGHRISE_BOT_TOKEN not set${NC}"
    MISSING_VARS=1
fi

if [ -z "$HIGHRISE_ROOM_ID" ]; then
    echo -e "${YELLOW}⚠️ HIGHRISE_ROOM_ID not set${NC}"
    MISSING_VARS=1
fi

# Yahan Zeno hata kar RADIO_PASSWORD kar diya gaya hai
if [ -z "$RADIO_PASSWORD" ]; then
    echo -e "${YELLOW}⚠️ RADIO_PASSWORD not set (Required for KingRadio)${NC}"
    MISSING_VARS=1
fi

if [ $MISSING_VARS -eq 0 ]; then
    echo -e "${GREEN}✅ All environment variables set${NC}"
else
    echo -e "${YELLOW}ℹ️ Tip: Set your KingRadio password using 'export RADIO_PASSWORD=your_pass'${NC}"
fi

echo ""
echo "============================================================"
echo -e "${GREEN}✨ Setup complete! Starting KingRadio Bot System...${NC}"
echo "============================================================"
echo ""

# Run the main script
python3 main.py
