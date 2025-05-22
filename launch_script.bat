@echo off
cd /d "%~dp0"
wt cmd /k "cd /d %~dp0 && python main.py"