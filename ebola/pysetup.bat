@echo off
REM Change directory to the project folder
cd /d "C:\Users\realr\Documents\Dev\Projects\wence\ebola"

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Downloading and installing Python...

    REM Define the Python installer URL and the installation directory
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe"
    set "PYTHON_INSTALLER=%TEMP%\python-installer.exe"
    set "PYTHON_DIR=C:\Python311"

    REM Download Python installer
    powershell -Command "Invoke-WebRequest -Uri %PYTHON_URL% -OutFile \"%PYTHON_INSTALLER%\""

    REM Run the installer silently
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 TargetDir="%PYTHON_DIR%"

    REM Cleanup the installer
    del "%PYTHON_INSTALLER%"

    REM Verify the installation
    "%PYTHON_DIR%\python.exe" --version >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        echo Python installation failed. Exiting.
        exit /b 1
    )

    REM Add Python to PATH for the current session
    set "PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%"
)

REM Upgrade pip to the latest version
python -m pip install --upgrade pip

REM Install dependencies from requirements.txt if it exists
IF EXIST "requirements.txt" (
    pip install -r requirements.txt
)

echo Dependencies have been set up successfully.
pause
