#!/usr/bin/env python3
"""
Setup NotebookLM Projects & Workspaces for all 64 projects.
Creates:
- <project_dir>/notebooklm/source_text.txt (Rich scientific source material for NotebookLM)
- <project_dir>/final_output/caption.txt (Clean Instagram caption with hashtags)
- Ensures watermark and thumbnail are ready
"""

import os
import sys
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
TELEPROMPTER_FILE = os.path.join(ROOT_DIR, "NASKAH_TELEPROMPTER_SIAP_REKAM.md")

def parse_teleprompter():
    """Mengambil naskah lengkap dari NASKAH_TELEPROMPTER_SIAP_REKAM.md"""
    if not os.path.exists(TELEPROMPTER_FILE):
        return {}
    
    with open(TELEPROMPTER_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern: ### <batch_num>. Project <num>: <title> ... up to next ###
    pattern = r'###\s+\d+\.\s+Project\s+(\d+):\s*([^\n]+)(.+?)(?=\n###|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    result = {}
    for p_num_str, title_str, body in matches:
        p_num = int(p_num_str)
        # Parse scenes
        scenes = []
        scene_matches = re.findall(r'\*\s+\*\*\[(Scene\s+\d+[^\]]*)\]\*\*\s*>\s*([^\n]+)', body)
        for s_header, s_text in scene_matches:
            clean_text = s_text.strip().strip('"').strip("'")
            scenes.append({"header": s_header.strip(), "text": clean_text})
        
        result[p_num] = {
            "title": title_str.strip(),
            "body": body.strip(),
            "scenes": scenes
        }
    return result

def clean_filename(title: str) -> str:
    """Membersihkan karakter ilegal untuk nama file."""
    clean = re.sub(r'[\\/*?:"<>|]', "", title)
    clean = re.sub(r'\s+', " ", clean).strip()
    return clean

def extract_instagram_caption(p_data: dict, p_dir: str) -> str:
    """Mengekstrak caption Instagram terformat."""
    sk = p_data.get("social_kit", {})
    caption = sk.get("instagram") or sk.get("caption")
    if not caption:
        cap_file = os.path.join(p_dir, "caption_instagram.txt")
        if not os.path.exists(cap_file):
            cap_file = os.path.join(p_dir, "caption.txt")
        if os.path.exists(cap_file):
            with open(cap_file, "r", encoding="utf-8") as cf:
                caption = cf.read().strip()
    
    if not caption:
        # Fallback dari title & scenes
        title = p_data.get("title", "")
        caption = f"{title} 🧠✨\n\nPernah overthinking soal hal ini? Simak penjelasannya sampai tuntas!\n\nSave reels ini & share ke temanmu ya! 👉\n\n#TemanOverthinking #SerunyaBelajar #taugaksih #faktaunik #fyp"
    
    return caption.strip()

def build_rich_source_text(p_id: str, p_data: dict, teleprompter_data: dict) -> str:
    """Menyusun teks artikel riset yang kaya & komprehensif untuk NotebookLM."""
    # Ambil nomor project dari ID (misal: 38 dari '38_kenapa_nyamuk_dengungin_kuping')
    match = re.match(r'^(\d+)_', p_id)
    p_num = int(match.group(1)) if match else 0
    
    title = p_data.get("title") or p_data.get("topic") or p_id
    
    lines = []
    lines.append("=" * 80)
    lines.append(f"DOKUMEN RISET & MATERI SUMBER KONTEN: {title.upper()}")
    lines.append("CHANNEL / SERI: Tanya Kenapa ?")
    lines.append("TARGET OUTPUT: Video Edukasi Singkat & Padat (~1 Menit)")
    lines.append("=" * 80)
    lines.append("")
    
    lines.append("## 1. Topik & Fenomena Utama")
    lines.append(f"Pertanyaan: \"{title}\"")
    lines.append("Fenomena ini adalah rasa penasaran sehari-hari yang sering dialami banyak orang namun jarang dipahami alasan ilmiah di baliknya.")
    lines.append("")
    
    # Masukkan materi naskah / scenes
    tele_info = teleprompter_data.get(p_num)
    if tele_info and tele_info.get("scenes"):
        lines.append("## 2. Poin Narasi & Struktur Pembahasan")
        for s in tele_info["scenes"]:
            lines.append(f"- **{s['header']}**:")
            lines.append(f"  \"{s['text']}\"")
            lines.append("")
    else:
        # Dari scenes project.json
        scenes = p_data.get("scenes", [])
        if scenes:
            lines.append("## 2. Poin Narasi & Struktur Pembahasan")
            for idx, s in enumerate(scenes, 1):
                stext = s.get("text", "")
                lines.append(f"- **Bagian {idx}**:")
                lines.append(f"  \"{stext}\"")
                lines.append("")
    
    lines.append("## 3. Penjelasan Sains & Konteks Mendalam")
    lines.append(f"Topik ini menjelaskan secara sains mengapa fenomena \"{title}\" terjadi.")
    lines.append("Tujuan konten adalah mengubah hal sepele menjadi 'AHA Moment' yang membuka wawasan penonton.")
    lines.append("Bahasa yang digunakan santai, komunikatif, to-the-point, dan mudah dipahami oleh masyarakat umum tanpa jargon rumit.")
    lines.append("")
    
    lines.append("## 4. Kata Kunci & Inti Pesan")
    lines.append(f"- Topik: {title}")
    lines.append("- Format: Video Short / Reels vertikal 9:16")
    lines.append("- Nada Bicara: Menghibur, penasaran, edukatif, dan ramah.")
    lines.append("")
    lines.append("=" * 80)
    
    return "\n".join(lines)

def setup_all_projects():
    tele_data = parse_teleprompter()
    print(f"Loaded {len(tele_data)} entries from teleprompter naskah.")
    
    projects = sorted([d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d)) and not d.startswith("_")])
    print(f"Processing {len(projects)} projects in {PROJECTS_DIR}...")
    
    count_setup = 0
    for p_id in projects:
        p_dir = os.path.join(PROJECTS_DIR, p_id)
        json_path = os.path.join(p_dir, "project.json")
        
        if not os.path.exists(json_path):
            continue
        
        with open(json_path, "r", encoding="utf-8") as f:
            p_data = json.load(f)
            
        title = p_data.get("title") or p_id
        
        # 1. Folder notebooklm
        nlm_dir = os.path.join(p_dir, "notebooklm")
        os.makedirs(nlm_dir, exist_ok=True)
        
        # 2. source_text.txt
        source_text = build_rich_source_text(p_id, p_data, tele_data)
        source_file = os.path.join(nlm_dir, "source_text.txt")
        with open(source_file, "w", encoding="utf-8") as sf:
            sf.write(source_text)
            
        # 3. Folder final_output
        final_dir = os.path.join(p_dir, "final_output")
        os.makedirs(final_dir, exist_ok=True)
        
        # 4. caption.txt di final_output
        caption = extract_instagram_caption(p_data, p_dir)
        final_caption_file = os.path.join(final_dir, "caption.txt")
        with open(final_caption_file, "w", encoding="utf-8") as cf:
            cf.write(caption)
            
        # 5. README bantuan di folder notebooklm
        help_file = os.path.join(nlm_dir, "PETUNJUK_PENGGUNAAN.txt")
        with open(help_file, "w", encoding="utf-8") as hf:
            hf.write(
                f"CARA PAKAI FOLDER INI UNTUK PROJECT: {title}\n"
                f"==========================================================\n"
                f"1. Buka NotebookLM (https://notebooklm.google.com/)\n"
                f"2. Buat notebook baru atau buka notebook 'Tanya Kenapa'\n"
                f"3. Upload / paste isi file 'source_text.txt' sebagai sumber bacaan.\n"
                f"4. Generate Video Overview / Audio Short di NotebookLM.\n"
                f"5. Download hasil videonya dari NotebookLM, lalu taruh file video (.mp4) di folder ini!\n"
                f"6. Jalankan script editor otomatis (python3 process_notebooklm.py) untuk:\n"
                f"   - Menghilangkan watermark NotebookLM & diganti watermark 'Tanya Kenapa ?'\n"
                f"   - Memotong 2-3 detik bumper out di ujung video\n"
                f"   - Menempelkan cover thumbnail 1 detik di awal video\n"
                f"   - Menyimpan hasil final ke folder 'final_output/' dengan nama: '{clean_filename(title)}.mp4'\n"
            )
            
        count_setup += 1
        
    print(f"Sukses mengonfigurasi {count_setup} project dengan folder 'notebooklm/' dan 'final_output/'!")

if __name__ == "__main__":
    setup_all_projects()
