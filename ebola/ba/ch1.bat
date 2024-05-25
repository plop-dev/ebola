@echo off
set "filePath=%windir%\System32\ebola.exe"

:loop
if exist "%filePath%" (
    echo File exists

    tasklist | find /i "ebola.exe" >nul

    if errorlevel 1 (
        echo Not running
        start "" "%filePath%"
    ) else (
        echo Running
    )
) else (
    echo File doesn't exist
)

rem wait for 60 sec
timeout /t 60 /nobreak >nul

rem go to start of loop
goto loop