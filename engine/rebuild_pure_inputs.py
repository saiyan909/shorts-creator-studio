#!/usr/bin/env python3
"""
Rework SEMUA_INPUT_NOTEBOOKLM.txt & individual input.txt files:
- 100% PURE content for NotebookLM (NO captions, NO meta-prompts)
- Contains ONLY: Title, Daily Phenomenon/Hook, Real Scientific Mechanism, AHA Analogy, Interactive Closing
- Clean and immediately copas-ready for all 64 topics.
"""

import os
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)
PROJECT_LM_DIR = os.path.join(BASE_DIR, "projectLM")
OLD_PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
TELEPROMPTER_FILE = os.path.join(ROOT_DIR, "NASKAH_TELEPROMPTER_SIAP_REKAM.md")

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

def get_clean_project_content(p_id: str, p_num: int, p_data: dict, tele_data: dict) -> str:
    title = p_data.get("title") or p_data.get("topic") or p_id
    
    # Khusus Project 03 (yang sudah di-polish secara presisi)
    if p_num == 3:
        return f"""TOPIK: {title}

FENOMENA SEHARI-HARI:
2 jam nongkrong bareng sahabat atau main game berasa cuma 10 menit, tapi giliran 10 menit nunggu antrean atau kelas membosankan rasanya lama banget berasa 2 jam.

PENJELASAN SAINS & MEKANISME OTAK:
1. Hormon Dopamin & Jam Biologis Internal (Internal Pacemaker):
   Saat kita melakukan hal yang sangat menyenangkan, otak melepaskan hormon dopamin dalam jumlah besar di area basal ganglia. Lonjakan dopamin ini memperlambat ritme "jam internal biologis" otak kita. Akibatnya, waktu objektif di dunia nyata terasa melesat jauh lebih cepat daripada persepsi internal kita.
2. Perhatian Selektif (Selective Attention & State of Flow):
   Persepsi waktu bergantung pada seberapa sering otak memeriksa penanda waktu. Saat bosan, otak kekurangan stimulasi kognitif sehingga terus-menerus sadar akan berlalunya detik demi detik ("kok lama banget ya?"). Sebaliknya saat bersenang-senang dan fokus penuh (flow state), kapasitas kognitif tersedot 100% ke aktivitas, sehingga otak sama sekali tidak mencatat penanda waktu.
3. Analogi Relativitas Einstein:
   "Duduk dua jam bersama orang yang kamu sukai terasa seperti dua menit. Tetapi duduk dua menit di atas kompor yang panas terasa seperti dua jam."
4. Paradoks Memori (Memory Paradox):
   Saat dijalani momen seru terasa singkat, tapi ketika diingat kembali di masa depan, momen liburan terasa sangat panjang dan kaya karena hipokampus merekam banyak stimulasi memori baru.

DISKUSI PENUTUP:
Menurutmu, momen apa dalam hidupmu yang berlalunya paling cepat tanpa disadari?"""

    # Cek apakah ada di teleprompter (Projects 22-64)
    tele_info = tele_data.get(p_num)
    if tele_info and tele_info.get("scenes"):
        scenes = tele_info["scenes"]
        # Format scenes into a cohesive narrative article
        hook = ""
        mitos = ""
        sains = ""
        analogi = ""
        cta = ""
        for s in scenes:
            hdr = s["header"].lower()
            txt = s["text"].strip('*').strip('"')
            if "hook" in hdr:
                hook = txt
            elif "mitos" in hdr or "kontras" in hdr:
                mitos = txt
            elif "sains" in hdr:
                sains = txt
            elif "analogi" in hdr or "aha" in hdr:
                analogi = txt
            elif "cta" in hdr or "call" in hdr:
                cta = txt

        parts = [f"TOPIK: {title}", ""]
        if hook:
            parts.append(f"FENOMENA & PERTANYAAN UTAMA:\n{hook}\n")
        if mitos:
            parts.append(f"MITOS VS REALITA:\n{mitos}\n")
        if sains:
            parts.append(f"PENJELASAN SAINS & ILMIAH:\n{sains}\n")
        if analogi:
            parts.append(f"MEKANISME & ANALOGI (AHA MOMENT):\n{analogi}\n")
        if cta:
            parts.append(f"KESIMPULAN & DISKUSI PENUTUP:\n{cta}")
        return "\n".join(parts).strip()

    # Projects 01-21 (dari scenes project.json)
    scenes = p_data.get("scenes", [])
    if scenes:
        parts = [f"TOPIK: {title}", ""]
        parts.append("RINGKASAN & PEMBAHASAN:")
        for idx, s in enumerate(scenes, 1):
            stext = s.get("text", "").strip()
            parts.append(f"• Bagian {idx}: {stext}")
        return "\n".join(parts).strip()

    return f"TOPIK: {title}"

def rebuild():
    tele_data = parse_teleprompter()
    projects = sorted([d for d in os.listdir(PROJECT_LM_DIR) if os.path.isdir(os.path.join(PROJECT_LM_DIR, d)) and not d.startswith("_")])
    
    print(f"Rebuilding pure NotebookLM inputs for {len(projects)} projects...")
    
    master_lines = []
    master_lines.append("=" * 80)
    master_lines.append(" PURE INPUT NOTEBOOKLM - SERI TANYA KENAPA ? (64 KONTEN)")
    master_lines.append(" File ini 100% murni materi riset & sains untuk langsung di-copas ke NotebookLM.")
    master_lines.append(" (Tanpa caption Instagram & tanpa instruksi prompt yang mengganggu)")
    master_lines.append("=" * 80)
    master_lines.append("")
    
    # Table of contents
    master_lines.append("DAFTAR ISI KONTEN (1 - 64):")
    for idx, p_id in enumerate(projects, 1):
        old_json = os.path.join(OLD_PROJECTS_DIR, p_id, "project.json")
        t = p_id
        if os.path.exists(old_json):
            with open(old_json, "r", encoding="utf-8") as f:
                t = json.load(f).get("title", p_id)
        master_lines.append(f"  #{idx:02d} -> {t}")
    master_lines.append("\n" + "=" * 80 + "\n")
    
    for idx, p_id in enumerate(projects, 1):
        old_json = os.path.join(OLD_PROJECTS_DIR, p_id, "project.json")
        p_data = {}
        if os.path.exists(old_json):
            with open(old_json, "r", encoding="utf-8") as f:
                p_data = json.load(f)
                
        content_text = get_clean_project_content(p_id, idx, p_data, tele_data)
        
        # Tambahkan ke Master File
        master_lines.append("=" * 80)
        master_lines.append(f"KONTEN #{idx:02d} (Folder: {p_id})")
        master_lines.append("=" * 80)
        master_lines.append(content_text)
        master_lines.append("")
        master_lines.append("")
        
        # Update file input.txt di masing-masing subfolder
        subfolder_input = os.path.join(PROJECT_LM_DIR, p_id, "input.txt")
        with open(subfolder_input, "w", encoding="utf-8") as sf:
            sf.write(content_text + "\n")

    # Tulis master file
    master_path = os.path.join(PROJECT_LM_DIR, "SEMUA_INPUT_NOTEBOOKLM.txt")
    with open(master_path, "w", encoding="utf-8") as mf:
        mf.write("\n".join(master_lines))
        
    print(f"Master file rebuilt: {master_path}")
    print(f"Total lines: {len(master_lines)} (100% murni materi, NO captions, NO prompts!)")

if __name__ == "__main__":
    rebuild()
