#!/usr/bin/env python3
"""
Adhi Studio - NotebookLM Video Remake Processor
Engine otomatis untuk mengedit video output dari NotebookLM:
1. Menyelipkan Cover Thumbnail (1.0 detik) di awal video
2. Memotong bumper out NotebookLM (2-3 detik) di ujung video
3. Memberikan sensor boxblur pada logo NotebookLM dan menempelkan watermark 'Tanya Kenapa ?' di pojok kanan bawah
4. Menyimpan video final ke folder 'final_output/<Judul Konten>.mp4' bersama 'caption.txt'
"""

import os
import sys
import re
import json
import glob
import subprocess
from typing import Optional, Dict, Any, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
WATERMARK_PATH = os.path.join(ASSETS_DIR, "branding", "watermark_tanya_kenapa.png")

def clean_filename(title: str) -> str:
    """Membersihkan karakter terlarang di filesystem untuk nama file video."""
    clean = re.sub(r'[\\/*?:"<>|]', "", title)
    clean = re.sub(r'\s+', " ", clean).strip()
    return clean

def get_video_duration(video_path: str) -> float:
    """Mendapatkan durasi video dalam detik via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    try:
        output = subprocess.check_output(cmd, text=True).strip()
        return float(output)
    except Exception as e:
        print(f"Gagal membaca durasi {video_path}: {e}")
        return 0.0

def find_raw_video(notebooklm_dir: str) -> Optional[str]:
    """Mencari file video raw mp4 di dalam folder notebooklm/."""
    if not os.path.exists(notebooklm_dir):
        return None
    candidates = glob.glob(os.path.join(notebooklm_dir, "*.mp4"))
    if not candidates:
        return None
    # Prioritaskan raw_video.mp4 atau file mp4 terbaru
    candidates.sort(key=os.path.getmtime, reverse=True)
    return candidates[0]

def process_notebooklm_video(
    project_id_or_path: str,
    bumper_cut_seconds: float = 3.0,
    intro_seconds: float = 1.0,
    watermark_pos: str = "bottom_right"
) -> Dict[str, Any]:
    """
    Memproses video NotebookLM untuk 1 project:
    - Input: <project_dir>/notebooklm/*.mp4
    - Output: <project_dir>/final_output/<Judul Konten>.mp4
    """
    if os.path.isabs(project_id_or_path) and os.path.isdir(project_id_or_path):
        p_dir = project_id_or_path
        p_id = os.path.basename(p_dir)
    else:
        # Cari project berdasarkan ID atau prefix
        target = project_id_or_path.strip()
        match_dirs = [d for d in os.listdir(PROJECTS_DIR) if d == target or d.startswith(f"{target}_") or d.startswith(f"{int(target):02d}_") if target.isdigit()]
        if not match_dirs:
            return {"success": False, "error": f"Project '{project_id_or_path}' tidak ditemukan."}
        p_dir = os.path.join(PROJECTS_DIR, match_dirs[0])
        p_id = match_dirs[0]

    json_path = os.path.join(p_dir, "project.json")
    if not os.path.exists(json_path):
        return {"success": False, "error": f"File project.json tidak ditemukan di {p_dir}."}

    with open(json_path, "r", encoding="utf-8") as f:
        p_data = json.load(f)

    title = p_data.get("title") or p_id
    clean_title = clean_filename(title)

    nlm_dir = os.path.join(p_dir, "notebooklm")
    raw_video = find_raw_video(nlm_dir)
    if not raw_video:
        return {
            "success": False,
            "project": p_id,
            "title": title,
            "error": f"Belum ada video output NotebookLM (.mp4) di folder: {nlm_dir}"
        }

    thumb_path = os.path.join(p_dir, "thumbnail.jpg")
    if not os.path.exists(thumb_path):
        # Fallback cari di output/
        alt_thumb = os.path.join(p_dir, "output", "thumbnail.jpg")
        if os.path.exists(alt_thumb):
            thumb_path = alt_thumb
        else:
            return {"success": False, "error": f"Thumbnail tidak ditemukan di {thumb_path}."}

    if not os.path.exists(WATERMARK_PATH):
        # Generate watermark jika belum ada
        from engine.create_watermark import generate_watermark
        generate_watermark(WATERMARK_PATH)

    final_dir = os.path.join(p_dir, "final_output")
    os.makedirs(final_dir, exist_ok=True)
    final_video_path = os.path.join(final_dir, f"{clean_title}.mp4")

    # 1. Analisis Durasi
    total_dur = get_video_duration(raw_video)
    if total_dur <= bumper_cut_seconds:
        cut_dur = total_dur
    else:
        cut_dur = total_dur - bumper_cut_seconds

    print(f"\n🎬 Memproses: [{p_id}] {title}")
    print(f"   📹 Raw Video   : {os.path.basename(raw_video)} ({total_dur:.1f}s)")
    print(f"   ✂️  Potong Bumper: {bumper_cut_seconds}s di akhir (Durasi main: {cut_dur:.1f}s)")
    print(f"   🖼️  Intro Thumb : {intro_seconds}s di awal")
    print(f"   🎯 Output File : final_output/{clean_title}.mp4")

    # 2. Filter Complex FFmpeg
    # [0:v] Thumbnail (loop intro_seconds)
    # [1:v] Main Video (trim 0 to cut_dur, scale/pad 1080x1920, blur patch watermark NotebookLM, overlay Tanya Kenapa)
    # [1:a] Audio Main (trim 0 to cut_dur)
    # [a0] Silent audio for thumbnail intro
    # Concat: [v0][a0] + [v1][a1]
    
    # Koordinat blur patch untuk watermark NotebookLM di pojok kanan bawah (1080x1920)
    # Ukuran patch 380x110 pada x=660, y=1750
    blur_x = 660
    blur_y = 1750
    blur_w = 380
    blur_h = 110

    filter_complex = f"""
    [0:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v0];
    anullsrc=r=44100:cl=stereo,atrim=0:{intro_seconds}[a0];
    [1:v]trim=0:{cut_dur},setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,split=2[main1][main2];
    [main2]crop={blur_w}:{blur_h}:{blur_x}:{blur_y},boxblur=20:5[blurred_patch];
    [main1][blurred_patch]overlay={blur_x}:{blur_y}[main_blurred];
    [main_blurred][2:v]overlay=W-w-35:H-h-50[v1];
    [1:a]atrim=0:{cut_dur},asetpts=PTS-STARTPTS[a1];
    [v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]
    """.strip()

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(intro_seconds), "-i", thumb_path,
        "-i", raw_video,
        "-i", WATERMARK_PATH,
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        final_video_path
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"❌ Error rendering {p_id}: {proc.stderr[-600:]}")
            return {"success": False, "project": p_id, "error": proc.stderr[-600:]}

        final_size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
        final_dur = get_video_duration(final_video_path)

        # Pastikan caption.txt tersedia di final_output
        caption_file = os.path.join(final_dir, "caption.txt")
        if not os.path.exists(caption_file):
            from engine.setup_notebooklm_projects import extract_instagram_caption
            cap = extract_instagram_caption(p_data, p_dir)
            with open(caption_file, "w", encoding="utf-8") as cf:
                cf.write(cap)

        print(f"✅ SUKSES! Video Final siap posting:")
        print(f"   📁 {final_video_path}")
        print(f"   ⏱️  Durasi: {final_dur:.1f} detik | 💾 Ukuran: {final_size_mb:.2f} MB\n")

        return {
            "success": True,
            "project": p_id,
            "title": title,
            "final_video": final_video_path,
            "caption_file": caption_file,
            "duration": final_dur,
            "size_mb": final_size_mb
        }
    except Exception as e:
        print(f"❌ Exception saat render {p_id}: {e}")
        return {"success": False, "project": p_id, "error": str(e)}

def process_batch(bumper_cut_seconds: float = 3.0, intro_seconds: float = 1.0) -> List[Dict[str, Any]]:
    """Memproses semua project yang sudah ada video di folder notebooklm/."""
    projects = sorted([d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d)) and not d.startswith("_")])
    ready_projects = []

    for p in projects:
        nlm_dir = os.path.join(PROJECTS_DIR, p, "notebooklm")
        raw = find_raw_video(nlm_dir)
        if raw:
            ready_projects.append(p)

    if not ready_projects:
        print("⚠️ Belum ada video NotebookLM yang ditemukan di folder project mana pun.")
        print("💡 Cara pakai: Taruh file video .mp4 hasil download dari NotebookLM ke dalam folder:")
        print("   adhi_studio/projects/<nama_project>/notebooklm/")
        return []

    print(f"🔍 Ditemukan {len(ready_projects)} project siap render!")
    results = []
    for pid in ready_projects:
        res = process_notebooklm_video(pid, bumper_cut_seconds=bumper_cut_seconds, intro_seconds=intro_seconds)
        results.append(res)
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if target in ["--all", "-a", "all"]:
            process_batch()
        else:
            process_notebooklm_video(target)
    else:
        print("=== Adhi Studio - NotebookLM Processor ===")
        print("Penggunaan:")
        print("  python3 notebooklm_processor.py <id_project>   (Contoh: python3 notebooklm_processor.py 38)")
        print("  python3 notebooklm_processor.py --all          (Proses semua project yang ada videonya)")
        # Coba auto detect apakah ada project ready
        process_batch()
