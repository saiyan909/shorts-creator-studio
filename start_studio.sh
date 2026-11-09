#!/bin/bash
# ==========================================
# LAUNCHER: ADHI STUDIO (Tanya Kenapa Engine)
# ==========================================
echo "============================================="
echo "   🚀 MEMULAI ADHI STUDIO: @tanya.kenapa    "
echo "============================================="

# Masuk ke direktori skrip ini berada
cd "$(dirname "$0")"

# Cek Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 tidak ditemukan. Harap instal Python 3 terlebih dahulu."
    exit 1
fi

# Cek virtual environment jika ada
if [ -d "venv" ]; then
    echo "📦 Mengaktifkan virtual environment (venv)..."
    source venv/bin/activate
fi

# Jalankan server
echo "✨ Menjalankan server di http://localhost:5050 ..."
python3 server.py &
SERVER_PID=$!

sleep 2

# Buka browser otomatis jika tersedia
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:5050"
elif command -v open &> /dev/null; then
    open "http://localhost:5050"
fi

echo "✅ Adhi Studio aktif! Buka browser di: http://localhost:5050"
echo "Tekan [Ctrl+C] untuk menghentikan server."

# Tunggu server berjalan
wait $SERVER_PID
