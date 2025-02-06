@echo off
tasklist | find /I "pythonw.exe"

if errorlevel 1 (
    start pythonw.exe "./main.py"
) else (
    taskkill /IM pythonw.exe /f
)