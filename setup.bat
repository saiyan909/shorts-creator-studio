@echo off
echo =======================================================
echo         ⚡ ADHI STUDIO - SETUP & RUNNER WINDOWS        
echo =======================================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan! Harap instal Python 3 dan centang 'Add Python to PATH'.
    pause
    exit /b 1
)

where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg belum terpasang di PATH Windows.
    echo Harap download ffmpeg dari https://ffmpeg.org/ dan masukkan ke System PATH.
)

echo [INFO] Menginstal dependensi Python...
pip install -r requirements.txt

echo [INFO] Menjalankan Adhi Studio di http://localhost:5050...
python server.py
pause
