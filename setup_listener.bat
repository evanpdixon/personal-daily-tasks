@echo off
REM RME Task Listener - Register as hidden background service
REM Right-click this file and select "Run as administrator"

echo.
echo  Task Listener - Setup
echo  =====================
echo.

schtasks /create /tn "RME Task Listener" /xml "%~dp0RMETaskListener.xml" /f

if %errorlevel%==0 (
    echo.
    echo  Task created! Listener runs hidden in the background.
    echo  It starts on logon and auto-restarts if it crashes.
    echo.
    echo  To run now:  schtasks /run /tn "RME Task Listener"
    echo  To stop:     schtasks /end /tn "RME Task Listener"
    echo  To check:    schtasks /query /tn "RME Task Listener"
    echo  To delete:   schtasks /delete /tn "RME Task Listener" /f
) else (
    echo.
    echo  ERROR: Could not create task. Make sure you ran this as Administrator.
)

echo.
pause
