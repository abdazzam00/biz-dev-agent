#!/usr/bin/env bash
set -e

REPO="https://github.com/abdazzam00/biz-dev-agent.git"
DIR="biz-dev-agent"

echo ""
echo " ____  ____       _                    _"
echo "| __ )|  _ \     / \   __ _  ___ _ __ | |_"
echo "|  _ \| | | |   / _ \ / _\` |/ _ \ '_ \| __|"
echo "| |_) | |_| |  / ___ \ (_| |  __/ | | | |_"
echo "|____/|____/  /_/   \_\__, |\___|_| |_|\__|"
echo "                      |___/"
echo ""
echo "Installing BD Agent..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo ""
    echo "Install Python 3.10+:"
    echo "  macOS:        brew install python@3.11"
    echo "  Ubuntu/Debian: sudo apt install python3.11 python3.11-venv python3-pip"
    echo "  Windows:      https://python.org/downloads"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo "Error: Python 3.10+ required. Found Python $PYTHON_VERSION"
    exit 1
fi

echo "Found Python $PYTHON_VERSION"

# Clone
if [ -d "$DIR" ]; then
    echo "Directory $DIR already exists. Pulling latest..."
    cd "$DIR"
    git pull origin main
else
    echo "Cloning repository..."
    git clone "$REPO"
    cd "$DIR"
fi

# Virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install
echo "Installing dependencies..."
pip install -e . --quiet

# Env file
if [ ! -f .env ]; then
    cp env.example .env
    echo ""
    echo "Created .env file. Add your API keys:"
    echo "  ANTHROPIC_API_KEY=your-key    (or OPENAI_API_KEY)"
    echo "  PERPLEXITY_API_KEY=your-key"
    echo ""
    echo "Edit with: nano .env"
fi

echo ""
echo "BD Agent installed successfully!"
echo ""
echo "To get started:"
echo "  cd $DIR"
echo "  source .venv/bin/activate"
echo "  bd-agent"
echo ""
