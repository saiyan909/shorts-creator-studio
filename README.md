# 🎬 Shorts Creator Studio: Automated Vertical Video & Audio Engine

> **End-to-End Vertical Video Production Engine**  
> An automated pipeline for vertical video creation (YouTube Shorts, TikTok, Instagram Reels, Facebook Reels) featuring 5-scene hook scripting, NotebookLM research formatting, dynamic ASS subtitle rendering, smart audio silence detection, minimalist thumbnail generation, and multi-platform caption packaging.

---

## 🌟 Architecture & Pipeline Overview

```
[1. Topic Ideation & Research]
             ↓
[2. 5-Scene Hook Scriptwriting] ➔ [3. NotebookLM Source Formatter]
             ↓
[4. Visual 9:16 Prompt Generator] ➔ [5. Voiceover & Smart Audio Silence Sync]
             ↓
[6. Dynamic ASS Subtitle Engine] ➔ [7. Minimalist Thumbnail Generator (PIL)]
             ↓
[8. Multi-Platform Captions & Memes] ➔ [9. FFmpeg MP4 Final Render (Ready-to-Post)]
```

### Key Modules:
1. **Dynamic Subtitle & Scene Synchronization (`engine/renderer.py`)**:
   * Uses FFmpeg `silencedetect` (-25dB threshold) to detect natural breath pauses.
   * Auto-splits video scene transitions on natural silence rather than cutting mid-sentence.
   * Compiles custom Advanced SubStation Alpha (`.ass`) subtitles with high-contrast outlines and vertical safe-zone positioning.
2. **Minimalist Vertical Thumbnail Engine (`engine/thumbnail.py`)**:
   * Programmatically draws 1080x1920 vertical covers using Python Pillow (PIL).
   * Generates dynamic dot-grid backgrounds, radial ambient aura, typography hooks, and geometric sparkle accents.
3. **Multi-Platform Content Packaging (`engine/draft_factory.py`, `engine/ai_generator.py`)**:
   * Automatically prepares tailored captions for YouTube Shorts, TikTok (max 5 hashtags), Instagram Reels, and Facebook.
   * Generates supplementary 4:5 meme formats for community cross-posting.
4. **Local Web Studio Dashboard (`server.py`, `web/`)**:
   * Python-powered lightweight HTTP server on port 5050.
   * Real-time preview player, project management, and one-click render interface.

---

## 📂 Project Structure

```text
shorts-creator-studio/
├── cli.py                     # Command-line interface runner
├── server.py                  # Web Studio backend server (Port 5050)
├── setup.sh                   # Environment setup script (Linux/macOS)
├── setup.bat                  # Environment setup script (Windows)
├── start_studio.sh            # Quick-launch dashboard script
├── requirements.txt           # Python dependencies
├── config.example.json        # Template configuration
├── schedule.example.json      # Template publishing schedule
├── engine/                    # Core processing engine
│   ├── renderer.py            # FFmpeg compiler & dynamic subtitle burn-in
│   ├── thumbnail.py           # Programmatic PIL thumbnail generator
│   ├── audio_processor.py     # Smart silence detection & audio sync
│   ├── ai_generator.py        # Script scenes & prompt generator
│   ├── draft_factory.py       # Batch draft pipeline
│   ├── meme_generator.py      # Cross-platform meme assembler
│   ├── tts.py                 # Edge-TTS voice synthesizer
│   ├── notebooklm_processor.py# NotebookLM video remake processor
│   └── project_manager.py     # Project CRUD & metadata manager
├── web/                       # Web Studio interface (HTML/CSS/JS)
├── assets/                    # Shared design fonts and meme templates
│   ├── fonts/                 # Poppins & Montserrat typography
│   ├── branding/              # Watermark templates
│   └── meme_templates/        # Viral meme template assets
└── projects/                  # Sample demonstration projects (01 - 05)
    ├── 01_es_tumbler_dingin/  # Full pipeline sample with rendered video
    ├── 02_kenapa_bapakbapak_kalau_bab/
    ├── 03_kenapa_waktu_cepet_pas_seneng/
    ├── 04_kenapa_bersin_berkali_kali/
    └── 05_kenapa_penghapus_gak_bisa_hapus_tinta/
```

---

## 🚀 Quick Start

### 1. Prerequisites
* **Python 3.10+**
* **FFmpeg** (with `ffprobe` installed and available in PATH)

### 2. Setup
```bash
./setup.sh
```
*(Or install dependencies manually via `pip install -r requirements.txt`).*

### 3. Launch Web Studio Dashboard
```bash
./start_studio.sh
# Or: python3 server.py
```
Open your browser at: **`http://localhost:5050`**

### 4. Render a Project via CLI
```bash
python3 cli.py --render 01_es_tumbler_dingin
```

---

## 🗺️ Active Roadmap
- [x] FFmpeg dynamic breath-pause scene alignment
- [x] Multi-platform caption & hashtag optimizer
- [x] Programmatic thumbnail generation with PIL
- [ ] Local Whisper AI integration for word-by-word karaoke subtitle animations
- [ ] Hardware acceleration support (NVENC / QuickSync / VAAPI)
- [ ] Automated B-roll clip retrieval and Ken Burns motion effects

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
