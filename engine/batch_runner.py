#!/usr/bin/env python3
"""
Adhi Studio - Batch Queue Runner
Otomatis memproses antrean video dari voiceover di assets/audio_record/.
Mendukung:
  python3 engine/batch_runner.py          -> Proses semua rekaman yang tersedia saat ini
  python3 engine/batch_runner.py --list   -> Cek status antrean rekaman & video
  python3 engine/batch_runner.py --watch  -> Background watcher (render otomatis saat file audio baru masuk)
"""

import os
import sys
import json
import glob
import time
import argparse
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
AUDIO_RECORD_DIR = os.path.join(BASE_DIR, "assets", "audio_record")

sys.path.insert(0, BASE_DIR)
from engine.renderer import render_project
from engine.audio_processor import enhance_and_trim_raw_voice
from engine.thumbnail import create_minimalist_thumbnail
from engine.ai_generator import clean_and_align_subtitles
from engine.image_fetcher import ensure_multi_images_for_project

def get_all_projects_status():
    results = []
    project_folders = sorted(glob.glob(os.path.join(PROJECTS_DIR, "*")))
    for p in project_folders:
        if not os.path.isdir(p) or os.path.basename(p).startswith(("_", ".")):
            continue
        json_path = os.path.join(p, "project.json")
        if not os.path.exists(json_path):
            continue
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        
        p_id = data.get("id", os.path.basename(p))
        title = data.get("title", p_id)
        audio_expected = data.get("audio_expected")
        
        audio_ready = False
        audio_source_path = None
        
        # Support flexible audio filenames: "22.mp3", "22_kentut.mp3", "kentut.mp3", etc.
        prefix_num = p_id.split('_')[0] if '_' in p_id else ""
        candidates = []
        
        if prefix_num and prefix_num.isdigit():
            candidates.extend([
                f"{prefix_num}.mp3",
                f"{int(prefix_num):02d}.mp3",
                f"{int(prefix_num)}.mp3",
                f"{prefix_num}.wav",
                f"{int(prefix_num):02d}.wav",
                f"{int(prefix_num)}.wav"
            ])
            
        if audio_expected:
            clean_name = re.sub(r'^\d+_', '', audio_expected)
            candidates.extend([
                audio_expected,
                clean_name,
                audio_expected.replace(".mp3", ".wav"),
                clean_name.replace(".mp3", ".wav")
            ])
            
        candidates.extend([
            f"{p_id}.mp3",
            f"{p_id}.wav",
            re.sub(r'^\d+_', '', f"{p_id}.mp3"),
            re.sub(r'^\d+_', '', f"{p_id}.wav")
        ])

        for c in candidates:
            cand = os.path.join(AUDIO_RECORD_DIR, c)
            if os.path.exists(cand) and os.path.getsize(cand) > 1000:
                audio_ready = True
                audio_source_path = cand
                break

        clean_voice = os.path.join(p, "audio", "voice_master_clean.mp3")
        if not audio_ready and os.path.exists(clean_voice):
            audio_ready = True
            audio_source_path = clean_voice

        output_video = os.path.join(p, "output", "final_shorts.mp4")
        is_rendered = os.path.exists(output_video)

        results.append({
            "id": p_id,
            "dir": p,
            "title": title,
            "audio_expected": audio_expected,
            "audio_ready": audio_ready,
            "audio_path": audio_source_path,
            "is_rendered": is_rendered,
            "data": data
        })
    return results

def print_queue_status():
    items = get_all_projects_status()
    print("\n" + "="*80)
    print(f"{'PROJECT ID':<35} | {'AUDIO EXPECTED':<18} | {'AUDIO':<10} | {'STATUS'}")
    print("="*80)
    for it in items:
        a_stat = "✅ READY" if it["audio_ready"] else "❌ BELUM"
        v_stat = "🎉 RENDERED" if it["is_rendered"] else ("⏳ IN QUEUE" if it["audio_ready"] else "💤 MENUNGGU AUDIO")
        print(f"{it['id']:<35} | {str(it['audio_expected']):<18} | {a_stat:<10} | {v_stat}")
    print("="*80 + "\n")

def process_single_project(item, force_rerender=False):
    p_id = item["id"]
    p_dir = item["dir"]
    data = item["data"]
    output_video = os.path.join(p_dir, "output", "final_shorts.mp4")

    if os.path.exists(output_video) and not force_rerender:
        print(f"[SKIP] {p_id} sudah selesai dirender: {output_video}")
        return True

    print(f"\n==================================================")
    print(f"🚀 [BATCH RUNNER] Memproses: {item['title']} ({p_id})")
    print(f"==================================================")

    # 1. Thumbnail
    thumb_path = os.path.join(p_dir, "thumbnail.jpg")
    if not os.path.exists(thumb_path):
        print(f"  [THUMBNAIL] Membuat thumbnail minimalis...")
        try:
            create_minimalist_thumbnail(item["title"], thumb_path)
        except Exception as e:
            print(f"  [THUMBNAIL WARNING] {e}")

    # 2. Check & Fetch Multi-Image Visuals (2-3 images per scene, min 10 images)
    print(f"  [VISUALS] Menyiapkan minimal 10 gambar HD dinamis (2-3 per scene) dari Web...")
    try:
        data = ensure_multi_images_for_project(data, p_dir, images_per_scene=2)
    except Exception as e_img:
        print(f"  [VISUAL WARNING] {e_img}")

    # 3. Audio Cleaning & Mastering
    clean_voice_path = os.path.join(p_dir, "audio", "voice_master_clean.mp3")
    audio_src = item["audio_path"]
    if not audio_src or not os.path.exists(audio_src):
        print(f"  [ERROR] File rekaman audio belum ditemukan: {item['audio_expected']}")
        return False

    if os.path.abspath(audio_src) != os.path.abspath(clean_voice_path):
        print(f"  [AUDIO] Membersihkan noise & mastering LUFS dari: {os.path.basename(audio_src)}...")
        enhance_and_trim_raw_voice(audio_src, clean_voice_path)
    else:
        print(f"  [AUDIO] Menggunakan audio master yang sudah bersih...")

    # 4. Align Subtitles
    data["scenes"] = clean_and_align_subtitles(data.get("scenes", []))
    with open(os.path.join(p_dir, "project.json"), "w", encoding="utf-8") as f_json:
        json.dump(data, f_json, indent=2, ensure_ascii=False)

    # 5. Render Video
    print(f"  [RENDER] Menjalankan engine render...")
    rendered_file = render_project(data, p_dir, custom_audio_path=clean_voice_path)

    # 6. Generate 3 Memes (9:16) & Captions di folder output/
    print(f"  [MEME & CAPTIONS] Memproses 3 foto meme + caption hook...")
    try:
        from engine.meme_generator import generate_project_memes_and_captions
        generate_project_memes_and_captions(p_id, p_dir, item["title"], data)
    except Exception as e_meme:
        print(f"  [MEME WARNING] Kendala pembuatan meme: {e_meme}")

    print(f"✨ [SUKSES] Seluruh paket konten ({p_id}) siap di folder output!\n")
    return True

def run_batch_once(force=False, range_str=None, project_id=None):
    items = get_all_projects_status()
    pending = [it for it in items if it["audio_ready"] and (not it["is_rendered"] or force)]
    
    if project_id:
        pending = [it for it in pending if project_id in it["id"]]
    elif range_str:
        try:
            parts = range_str.split("-")
            start_r, end_r = int(parts[0]), int(parts[1])
            filtered = []
            for it in pending:
                prefix = it["id"].split('_')[0]
                if prefix.isdigit() and start_r <= int(prefix) <= end_r:
                    filtered.append(it)
            pending = filtered
        except Exception as e:
            print(f"Format range tidak valid ({range_str}): {e}")

    if not pending:
        print("\n[BATCH RUNNER] Tidak ada proyek dengan audio siap render saat ini.")
        print(f"Taruh file audio rekaman di: {AUDIO_RECORD_DIR}")
        print("Gunakan 'python3 engine/batch_runner.py --list' untuk melihat nama file yang ditunggu.\n")
        return

    print(f"\n🎯 [BATCH RUNNER] Ditemukan {len(pending)} video siap render! Memulai proses berurutan...\n")
    for idx, item in enumerate(pending, 1):
        print(f"--- [TUGAS {idx}/{len(pending)}] ---")
        try:
            process_single_project(item, force_rerender=force)
        except Exception as e:
            print(f"❌ [ERROR GAGAL] Proyek {item['id']} mengalami kendala: {e}")

    print("🏁 [BATCH RUNNER] Seluruh antrean yang siap telah selesai diproses!\n")

def watch_mode():
    print(f"\n👀 [WATCH MODE AKTIF] Memantau folder {AUDIO_RECORD_DIR}...")
    print("Export rekaman dari Audacity langsung ke folder tersebut, sistem akan otomatis merender!\nTekan Ctrl+C untuk berhenti.\n")
    try:
        while True:
            items = get_all_projects_status()
            pending = [it for it in items if it["audio_ready"] and not it["is_rendered"]]
            if pending:
                print(f"\n⚡ [AUDIO BARU TERDETEKSI] Menemukan {len(pending)} tugas baru...")
                for item in pending:
                    try:
                        process_single_project(item)
                    except Exception as e:
                        print(f"❌ Error: {e}")
            time.sleep(4)
    except KeyboardInterrupt:
        print("\nWatcher dihentikan.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adhi Studio Batch Video Queue Runner")
    parser.add_argument("--list", action="store_true", help="Tampilkan status antrean semua project")
    parser.add_argument("--watch", action="store_true", help="Mode pemantauan otomatis (watch folder)")
    parser.add_argument("--force", action="store_true", help="Paksa render ulang video yang sudah jadi")
    parser.add_argument("--range", type=str, help="Rentang project nomor urut (contoh: 22-51)")
    parser.add_argument("--project", type=str, help="Render spesifik satu project ID / nomor")
    args = parser.parse_args()

    if args.list:
        print_queue_status()
    elif args.watch:
        watch_mode()
    else:
        run_batch_once(force=args.force, range_str=args.range, project_id=args.project)
