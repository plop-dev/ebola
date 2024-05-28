@echo off
setlocal

REM Define the URL and the installer file name
set "url=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
set "installer=python-3.11.9-amd64.exe"
set "max_attempts=5"
set "attempt=0"

python --version >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
    :download
    set /a attempt+=1

    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%url%', '%installer%')"

    if exist %installer% (
        goto install
    )

    if %attempt% lss %max_attempts% (
        goto download
    ) else (
        exit /b 1
    )

    :install
    %installer% /quiet InstallAllUsers=1 PrependPath=1

    del %installer%
)

cd /d "%windir%\System32\ebola"
python -m pip install --upgrade pip
IF EXIST "requirements.txt" (
    pip install -r requirements.txt
)

endlocal
exit /b 0
