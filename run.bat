@echo off
REM Set console to UTF-8 encoding for proper Arabic text support
chcp 65001 > nul
echo Starting Document QA Agent with UTF-8 support...
python run.py
