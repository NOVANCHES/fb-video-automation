@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo =================================================================
echo  MONITOREO DE MONETIZACION EN VIVO (BRUNO SCHILLER)
echo  YouTube Partner Program + Facebook Meta for Creators
echo =================================================================
echo.
.\.venv\Scripts\python.exe -u monetization_tracker.py
echo.
pause
