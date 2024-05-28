@echo off

FOR /F "delims=" %%i IN ('C:\Windows\System32\tasklist.exe /fo table /fi "IMAGENAME eq pythonw3.11.exe"') DO set output=%%i

if "%output%" == "INFO: No tasks are running which match the specified criteria." (
    start ..\ebola.bat
)

exit
