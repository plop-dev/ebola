@echo off
setlocal enabledelayedexpansion
set ip=145.40.191.247
echo Checking for open UDP, TCP-UDP, and TCP ports on %ip%...
echo.

:: Check for open TCP ports for the specific IP
echo Open TCP Ports on %ip%:
for /f "tokens=1,2,3,4,5" %%a in ('netstat -an ^| find "LISTENING" ^| find "TCP" ^| find "%ip%"') do (
    echo %%a %%b %%c %%d %%e
)
echo.

:: Check for open UDP ports for the specific IP
echo Open UDP Ports on %ip%:
for /f "tokens=1,2,3,4,5" %%a in ('netstat -an ^| find "UDP" ^| find "%ip%"') do (
    echo %%a %%b %%c %%d %%e
)
echo.

pause
endlocal
