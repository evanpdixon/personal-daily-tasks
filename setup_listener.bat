@echo off
REM RME Task Listener - Register as background task
REM Right-click this file and select "Run as administrator"

echo.
echo  Task Listener - Setup
echo  =====================
echo.

schtasks /create /tn "RME Task Listener" /tr "python C:\Claude\personal-daily-tasks\listener.py" /sc onstart /rl LIMITED /f

if %errorlevel%==0 (
    echo.
    echo  Task created! Listener will start on boot.
    echo.
    echo  To run now:  schtasks /run /tn "RME Task Listener"
    echo  To verify:   schtasks /query /tn "RME Task Listener"
    echo  To stop:     schtasks /end /tn "RME Task Listener"
    echo  To delete:   schtasks /delete /tn "RME Task Listener" /f
) else (
    echo.
    echo  ERROR: Could not create task. Make sure you ran this as Administrator.
)

echo.
pause
