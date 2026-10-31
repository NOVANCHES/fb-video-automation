@echo off
cd /d "%~dp0"
.\.venv\Scripts\python.exe uploader.py --video output/video_final.mp4
pause
