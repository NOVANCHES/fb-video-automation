@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo =================================================================
echo  CREADOR Y PUBLICADOR MULTI-RED (BRUNO SCHILLER)
echo  Facebook Reels + YouTube Shorts
echo =================================================================
echo.
set /p TOPIC="Escribe el tema (Enter para elegir automaticamente segun rotacion): "
if "%TOPIC%"=="" set TOPIC=auto
set /p FORMAT="Formato: video, photo, text o auto (Enter para auto): "
if "%FORMAT%"=="" set FORMAT=auto

.\.venv\Scripts\python.exe -u main.py --topic "%TOPIC%" --format "%FORMAT%" --headless
echo.
pause
