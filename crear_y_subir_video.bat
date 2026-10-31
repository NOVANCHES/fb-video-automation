@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo =================================================================
echo  AUTOMATIZADOR DE VIDEOS PARA FACEBOOK (ERPA VARDE)
echo =================================================================
set /p TOPIC="Escribe el tema del nuevo video (ej. 3 misterios del oceano): "
if "%TOPIC%"=="" set TOPIC=3 datos curiosos que parecen mentira
set /p CAPTION="Escribe la descripcion para Facebook (Enter para usar automatica): "
if "%CAPTION%"=="" set CAPTION=%TOPIC% - Siguenos en ERPA VARDE #reels #curiosidades #viral

.\.venv\Scripts\python.exe -u main.py --topic "%TOPIC%" --caption "%CAPTION%" --headless
echo.
pause
