@echo off
title Renovar Token de YouTube Shorts
cd /d "C:\Users\olou1\.gemini\antigravity\scratch\fb-video-automation"
echo =========================================================
echo    RENOVACION DE TOKEN DE YOUTUBE PARA BRUNO SCHILLER
echo =========================================================
echo.
echo Abriendo navegador para iniciar sesion con tu cuenta de Google...
echo.
.\.venv\Scripts\python.exe get_yt_token.py
echo.
pause
