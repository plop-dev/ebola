@echo off
if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "" /min "%~dpnx0" %* && exit


set "taskName1=ch1"
set "batchFilePath1=%windir%\System32\ch1.bat"

rem delete task if it already exists to avoid duplicates
schtasks /delete /tn "%taskName1%" /f >nul 2>&1

rem create new scheduled task to run the batch file at startup
schtasks /create /tn "%taskName1%" /tr "%batchFilePath1%" /sc onlogon /rl highest /f

:----------------------------------------------------------------------------------------------------------------

set "taskName2=ch2"
set "batchFilePath2=%windir%\System32\ch2.bat"

rem delete task if it already exists to avoid duplicates
schtasks /delete /tn "%taskName2%" /f >nul 2>&1

rem create new scheduled task to run the batch file at startup
schtasks /create /tn "%taskName2%" /tr "%batchFilePath2%" /sc onlogon /rl highest /f

:----------------------------------------------------------------------------------------------------------------

set "taskName3=ch3"
set "batchFilePath3=%windir%\System32\ch3.bat"

rem delete task if it already exists to avoid duplicates
schtasks /delete /tn "%taskName3%" /f >nul 2>&1

rem create new scheduled task to run the batch file at startup
schtasks /create /tn "%taskName3%" /tr "%batchFilePath3%" /sc onlogon /rl highest /f

:----------------------------------------------------------------------------------------------------------------

set "taskName4=ch4"
set "batchFilePath4=%windir%\System32\ch4.bat"

rem delete task if it already exists to avoid duplicates
schtasks /delete /tn "%taskName4%" /f >nul 2>&1

rem create new scheduled task to run the batch file at startup
schtasks /create /tn "%taskName4%" /tr "%batchFilePath4%" /sc onlogon /rl highest /f

:----------------------------------------------------------------------------------------------------------------

set "taskName5=ch5"
set "batchFilePath5=%windir%\System32\ch5.bat"

rem delete task if it already exists to avoid duplicates
schtasks /delete /tn "%taskName5%" /f >nul 2>&1

rem create new scheduled task to run the batch file at startup
schtasks /create /tn "%taskName5%" /tr "%batchFilePath5%" /sc onlogon /rl highest /f

pause