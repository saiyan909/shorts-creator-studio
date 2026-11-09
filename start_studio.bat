@echo off
title Adhi Studio - @tanya.kenapa
echo =============================================
echo    MEMULAI ADHI STUDIO: @tanya.kenapa
echo =============================================
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan di PATH sistem.
    echo Harap instal Python dari https://python.org dan centang "Add Python to PATH".
    pause
    exit /b
)

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo Menjalankan dashboard studio di http://localhost:5050 ...
start "" http://localhost:5050
python server.py
pause
