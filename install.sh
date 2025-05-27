#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Installing DhammaShell...${NC}"

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
python3 -m venv ~/.dhammashell
source ~/.dhammashell/bin/activate

# Install the package
pip install --upgrade pip
pip install -e .

# Add to shell profile
SHELL_RC=""
if [ -f ~/.bashrc ]; then
    SHELL_RC=~/.bashrc
elif [ -f ~/.zshrc ]; then
    SHELL_RC=~/.zshrc
fi

if [ -n "$SHELL_RC" ]; then
    echo "# DhammaShell" >> "$SHELL_RC"
    echo "alias ds='source ~/.dhammashell/bin/activate && ds'" >> "$SHELL_RC"
fi

echo -e "${GREEN}DhammaShell has been installed successfully!${NC}"
echo -e "Run ${BLUE}ds --help${NC} to see available commands."
echo -e "Run ${BLUE}ds --chat${NC} to start chatting mindfully." 