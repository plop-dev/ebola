@echo off
REM Change directory to the project folder
cd /d "C:\path\to\your\project"

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM Create a virtual environment in the project folder if it doesn't exist
IF NOT EXIST "venv" (
    python -m venv venv
)

REM Activate the virtual environment
CALL venv\Scripts\activate

REM Upgrade pip to the latest version
python -m pip install --upgrade pip

REM Install dependencies from requirements.txt if it exists
IF EXIST "requirements.txt" (
    pip install -r requirements.txt
)

REM Install specific dependencies directly (optional)
REM pip install somepackage anotherpackage

REM Deactivate the virtual environment
CALL venv\Scripts\deactivate

echo Dependencies have been set up successfully.
pause
