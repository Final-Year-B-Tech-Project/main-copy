@echo off
echo ========================================
echo CLEARING CACHE AND RESTARTING SERVER
echo ========================================

cd "ai_interview_system\Backend Files"

echo.
echo [1/3] Clearing Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

echo.
echo [2/3] Clearing Flask cache...
if exist "instance\*.db-journal" del /q "instance\*.db-journal"

echo.
echo [3/3] Starting Flask server...
echo.
echo ========================================
echo Server starting... Press Ctrl+C to stop
echo ========================================
echo.

python run.py

pause
