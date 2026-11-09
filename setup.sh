#!/usr/bin/env bash
set -e

echo "======================================================="
echo "        ⚡ ADHI STUDIO - SETUP & RUNNER SCRIPT         "
echo "======================================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 tidak ditemukan. Harap instal Python 3 terlebih dahulu."
    exit 1
fi

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg tidak terdeteksi di PATH."
    echo "   Untuk Linux (Ubuntu/Debian): sudo apt install -y ffmpeg"
    echo "   Untuk macOS: brew install ffmpeg"
fi

echo "📦 Memeriksa & menginstal dependency Python..."
pip install -r requirements.txt --break-system-packages 2>/dev/null || pip install -r requirements.txt

echo "🚀 Menjalankan Adhi Studio Server di port 5050..."
python3 server.py
