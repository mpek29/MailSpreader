#!/bin/bash

# Se positionner dans le dossier du script .sh
cd "$(dirname "$0")" || { echo "[ERROR] Failed to change directory"; exit 1; }
echo "[INFO] Current directory: $(pwd)"

# === Creates and activates the virtual environment, installs dependencies, and runs the Python script ===

# Check if the virtual environment folder exists
if [ ! -d "./venv" ]; then
    echo "[INFO] Virtual environment not found, creating..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create the virtual environment"
        exit 1
    fi
fi

# Activate the virtual environment
# shellcheck source=/dev/null
source ./venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate the virtual environment"
    exit 1
fi

# Check pip version and log output
echo "[INFO] Checking pip version..."
pip --version > pip_version.log 2>&1
cat pip_version.log
if [ $? -ne 0 ]; then
    echo "[ERROR] pip not found or failed to run. Check pip_version.log"
    exit 1
fi

# Install dependencies with full output logged
echo "[INFO] Installing dependencies..."
pip install -r requirements.txt > pip_install.log 2>&1
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies — see pip_install.log"
    cat pip_install.log
    exit 1
fi

# Run the Python script and log output
echo "[INFO] Running main.py..."
python ./main.py
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to execute main.py — see main_run.log"
    cat main_run.log
    exit 1
fi

# Done
echo "[SUCCESS] Script completed successfully"
