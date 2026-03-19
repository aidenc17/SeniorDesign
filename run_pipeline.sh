#!/bin/bash

# Death Star Detection Pipeline
# Runs image detection, then run transmsion, then upload script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# grab directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# configuration - all paths relative to script location
DETECTION_SCRIPT="$SCRIPT_DIR/image-detection/detection_script.py"
DETECTED_IMAGES_ZIP="$SCRIPT_DIR/image-detection/detected_images.zip"
LOG_FILE="$SCRIPT_DIR/pipeline.log"

# find venv - check common locations
if [ -d "$SCRIPT_DIR/venv" ]; then
    VENV_PATH="$SCRIPT_DIR/venv"
elif [ -d "$SCRIPT_DIR/../venv" ]; then
    VENV_PATH="$SCRIPT_DIR/../venv"
elif [ -d "$SCRIPT_DIR/../../venv" ]; then
    VENV_PATH="$SCRIPT_DIR/../../venv"
else
    echo -e "${RED}ERROR: Could not find virtual environment${NC}"
    echo "Searched in:"
    echo "  - $SCRIPT_DIR/venv"
    echo "  - $SCRIPT_DIR/../venv"
    echo "  - $SCRIPT_DIR/../../venv"
    exit 1
fi

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}Death Star Detection Pipeline${NC}"
echo -e "${BLUE}======================================${NC}\n"

# start logging
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "[$(date)] Starting pipeline..."
echo "Working directory: $SCRIPT_DIR"


# activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
echo "Venv location: $VENV_PATH"

# activate venv
source "$VENV_PATH/bin/activate"
echo -e "${GREEN} Virtual environment activated${NC}"


# step 1: running Detection Script
echo -e "\n${YELLOW}[STEP 1/2]${NC} Running image detection..."
echo "Script: $DETECTION_SCRIPT"
echo "---"

if [ ! -f "$DETECTION_SCRIPT" ]; then
    echo -e "${RED}ERROR: Detection script not found: $DETECTION_SCRIPT${NC}"
    exit 1
fi

# run detection script
if python3 "$DETECTION_SCRIPT"; then
    echo -e "${GREEN} Detection completed successfully${NC}"
else
    echo -e "${RED} Detection script failed${NC}"
    exit 1
fi


# step 2: verify ZIP was created
echo -e "\n${YELLOW}Verifying output...${NC}"

if [ ! -f "$DETECTED_IMAGES_ZIP" ]; then
    echo -e "${RED}ERROR: ZIP file not created: $DETECTED_IMAGES_ZIP${NC}"
    exit 1
fi

ZIP_SIZE=$(du -h "$DETECTED_IMAGES_ZIP" | cut -f1)
echo -e "${GREEN} ZIP file created: $DETECTED_IMAGES_ZIP ($ZIP_SIZE)${NC}"


# step 3: running transmission scripts
echo -e "\n${YELLOW}${NC} Running RF sender..."

SENDER_SCRIPT="$SCRIPT_DIR/RF-sender/sender.py"
echo "Script: $SENDER_SCRIPT"
echo "---"

if [ ! -f "$SENDER_SCRIPT" ]; then
    echo -e "${RED}ERROR: Sender script not found: $SENDER_SCRIPT${NC}"
    exit 1
fi

# run sender script
if python3 "$SENDER_SCRIPT"; then
    echo -e "${GREEN} RF sender completed successfully${NC}"
else
    echo -e "${RED} RF sender script failed${NC}"
    exit 1
fi


# step 4: running AWS upload script
echo -e "\n${YELLOW}[STEP 3/3]${NC} AWS upload (TODO)${NC}"


# pipeline complete
echo -e "\n${BLUE}======================================${NC}"
echo -e "${GREEN}Pipeline completed successfully!${NC}"
echo -e "${BLUE}======================================${NC}"
echo "[$(date)] Pipeline finished"
echo "Log saved to: $LOG_FILE"

# deactivate venv
deactivate