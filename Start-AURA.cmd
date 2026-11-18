@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -NoLogo -ExecutionPolicy Bypass -File "%~dp0scripts\start-workspace.ps1"
if errorlevel 1 pause
