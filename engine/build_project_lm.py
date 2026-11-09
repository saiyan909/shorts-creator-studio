#!/usr/bin/env python3
"""
Build adhi_studio/projectLM workspace:
1. Creates /home/integer009/PROJECTS/adhi_studio_portable/adhi_studio/projectLM
2. Creates SEMUA_INPUT_NOTEBOOKLM.txt (Semua 64 konten dalam 1 file txt siap copas)
3. Creates individual project folders under projectLM/ with input.txt, caption.txt, thumbnail.jpg, final/
"""

import os
import sys
import re
import json
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)
OLD_PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
PROJECT_LM_DIR = os.path.join(BASE_DIR, "projectLM")
TELEPROMPTER_FILE = os.path.join(ROOT_DIR, "NASKAH_TELEPROMPTER_SIAP_REKAM.md")

os.makedirs(PROJECT_LM_DIR, exist_ok=True)

def parse_teleprompter():
    if not os.path.exists(TELEPROMPTER_FILE):
        return {}
    with open(TELEPROMPTER_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r'###\s+\d+\.\s+Project\s+(\d+):\s*([^\n]+)(.+?)(?=\n###|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)
    result = {}
    for p_num_str, title_str, body in matches:
        p_num = int(p_num_str)
        scenes = []
        scene_matches = re.findall(r'\*\s+\*\*\[(Scene\s+\d+[^\]]*)\]\*\*\s*>\s*([^\n]+)', body)
        for s_header, s_text in scene_matches:
            clean_text = s_text.strip().strip('"').strip("'")
            scenes.append({"header": s_header.strip(), "text": clean_text})
        result[p_num] = {
            "title": title_str.strip(),
            "scenes": scenes
        }
    return result

def extract_instagram_caption(p_data: dict, p_dir: str) -> str:
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
        title = p_data.get("title", "")
        caption = f"{title} 🧠✨\n\nPernah overthinking soal hal ini? Simak penjelasannya sampai tuntas!\n\nSave reels ini & share ke sahabatmu ya! 👉\n\n#TemanOverthinking #SerunyaBelajar #taugaksih #faktaunik #fyp"
    return caption.strip()

def build_project_input_text(p_id: str, p_data: dict, teleprompter_data: dict) -> str:
    match = re.match(r'^(\d+)_', p_id)
    p_num = int(match.group(1)) if match else 0
    title = p_data.get("title") or p_data.get("topic") or p_id

    lines = []
    lines.append(f"TOPIK RISET KONTEN: {title}")
    lines.append("SERI: Tanya Kenapa ? | FORMAT: Edukasi Singkat & Padat (~1 Menit)")
    lines.append("-" * 70)
    lines.append(f"Pertanyaan Utama: \"{title}\"")
    lines.append("")
    
    # Masukkan materi naskah / scenes
    tele_info = teleprompter_data.get(p_num)
    if tele_info and tele_info.get("scenes"):
        lines.append("POIN-POIN PEMBAHASAN:")
        for s in tele_info["scenes"]:
            lines.append(f"• {s['header']}: \"{s['text']}\"")
    else:
        scenes = p_data.get("scenes", [])
        if scenes:
            lines.append("POIN-POIN PEMBAHASAN:")
            for idx, s in enumerate(scenes, 1):
                lines.append(f"• Bagian {idx}: \"{s.get('text', '')}\"")
                
    lines.append("")
    lines.append("PENJELASAN ILMIAH & KONTEKS:")
    lines.append(f"Fenomena \"{title}\" sering terjadi dalam kehidupan sehari-hari dan membuat penasaran.")
    lines.append("Jelaskan secara ilmiah dengan bahasa santai, to-the-point, dan berikan analogi yang mudah dipahami.")
    lines.append("Akhiri dengan pertanyaan interaktif yang memicu komentar penonton.")
    lines.append("-" * 70)
    
    return "\n".join(lines)

def build_all():
    tele_data = parse_teleprompter()
    projects = sorted([d for d in os.listdir(OLD_PROJECTS_DIR) if os.path.isdir(os.path.join(OLD_PROJECTS_DIR, d)) and not d.startswith("_")])
    
    print(f"Building projectLM for {len(projects)} projects...")
    
    master_lines = []
    master_lines.append("=" * 80)
    master_lines.append(" MASTER INPUT NOTEBOOKLM - SERI TANYA KENAPA ? (64 KONTEN)")
    master_lines.append(" File ini berisi seluruh materi riset untuk di-copy paste ke NotebookLM.")
    master_lines.append("=" * 80)
    master_lines.append("")
    
    # Table of Contents
    master_lines.append("DAFTAR ISI KONTEN:")
    for idx, p_id in enumerate(projects, 1):
        old_dir = os.path.join(OLD_PROJECTS_DIR, p_id)
        with open(os.path.join(old_dir, "project.json"), "r", encoding="utf-8") as f:
            pdata = json.load(f)
        t = pdata.get("title", p_id)
        master_lines.append(f"  [{idx:02d}] {p_id} -> {t}")
    master_lines.append("\n" + "=" * 80 + "\n")

    for idx, p_id in enumerate(projects, 1):
        old_dir = os.path.join(OLD_PROJECTS_DIR, p_id)
        with open(os.path.join(old_dir, "project.json"), "r", encoding="utf-8") as f:
            p_data = json.load(f)
            
        title = p_data.get("title", p_id)
        input_text = build_project_input_text(p_id, p_data, tele_data)
        caption = extract_instagram_caption(p_data, old_dir)
        
        # Tambahkan ke Master File
        master_lines.append("=" * 80)
        master_lines.append(f"KONTEN #{idx:02d}: {title.upper()} (Folder: {p_id})")
        master_lines.append("=" * 80)
        master_lines.append("")
        master_lines.append(">>> TEKS INPUT NOTEBOOKLM (TINGGAL COPAS KE NOTEBOOKLM):")
        master_lines.append(input_text)
        master_lines.append("")
        master_lines.append(">>> CAPTION INSTAGRAM:")
        master_lines.append(caption)
        master_lines.append("")
        master_lines.append("\n")
        
        # Buat folder individual di projectLM/
        lm_proj_dir = os.path.join(PROJECT_LM_DIR, p_id)
        os.makedirs(lm_proj_dir, exist_ok=True)
        os.makedirs(os.path.join(lm_proj_dir, "final"), exist_ok=True)
        
        # 1. input.txt
        with open(os.path.join(lm_proj_dir, "input.txt"), "w", encoding="utf-8") as f:
            f.write(input_text)
            
        # 2. caption.txt
        with open(os.path.join(lm_proj_dir, "caption.txt"), "w", encoding="utf-8") as f:
            f.write(caption)
            
        # 3. copy thumbnail.jpg
        old_thumb = os.path.join(old_dir, "thumbnail.jpg")
        if os.path.exists(old_thumb):
            shutil.copy2(old_thumb, os.path.join(lm_proj_dir, "thumbnail.jpg"))
            
        # 4. info file
        with open(os.path.join(lm_proj_dir, "README.txt"), "w", encoding="utf-8") as f:
            f.write(
                f"PROJECT LM: {title}\n"
                f"--------------------------------------------------\n"
                f"1. input.txt      -> Teks riset untuk di-copas ke NotebookLM\n"
                f"2. thumbnail.jpg  -> Cover thumbnail (diselipkan 1s di awal video)\n"
                f"3. Taruh video hasil NotebookLM (.mp4) langsung di folder ini!\n"
                f"4. Jalankan: ./process_projectLM.py {idx}\n"
                f"5. Hasil video matang & caption akan ada di folder: final/\n"
            )

    # Simpan master file
    master_path = os.path.join(PROJECT_LM_DIR, "SEMUA_INPUT_NOTEBOOKLM.txt")
    with open(master_path, "w", encoding="utf-8") as mf:
        mf.write("\n".join(master_lines))
        
    print(f"Master file saved: {master_path} ({len(master_lines)} lines)")
    print(f"All 64 projects configured cleanly under {PROJECT_LM_DIR}!")

if __name__ == "__main__":
    build_all()
