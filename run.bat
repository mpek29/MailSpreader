@echo off

REM Se positionner dans le dossier du script .bat
cd /d %~dp0
echo [INFO] Current directory: %cd%

REM === Creates and activates the virtual environment, installs dependencies, and runs the Python script ===

REM Check if the virtual environment folder exists
IF NOT EXIST ".\venv" (
    echo [INFO] Virtual environment not found, creating...
    python -m venv venv
    IF ERRORLEVEL 1 (
        echo [ERROR] Failed to create the virtual environment
        pause
        exit /b 1
    )
)

REM Check if the activation script exists
IF NOT EXIST ".\venv\Scripts\activate.bat" (
    echo [ERROR] Activation script not found: .\venv\Scripts\activate.bat
    pause
    exit /b 1
)

REM Activate the virtual environment
call ".\venv\Scripts\activate.bat"
IF ERRORLEVEL 1 (
    echo [ERROR] Failed to activate the virtual environment
    pause
    exit /b 1
)

REM Check pip version and log output
echo [INFO] Checking pip version...
pip --version > pip_version.log 2>&1
type pip_version.log

IF ERRORLEVEL 1 (
    echo [ERROR] pip not found or failed to run. Check pip_version.log
    pause
    exit /b 1
)

REM Install dependencies with full output logged
echo [INFO] Installing dependencies...
pip install -r requirements.txt > pip_install.log 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Failed to install dependencies — see pip_install.log
    type pip_install.log
    pause
    exit /b 1
)

REM Run the Python script and log output
echo [INFO] Running main.py...
python .\main.py
IF ERRORLEVEL 1 (
    echo [ERROR] Failed to execute main.py — see main_run.log
    type main_run.log
    pause
    exit /b 1
)

REM Done
echo [SUCCESS] Script completed successfully
