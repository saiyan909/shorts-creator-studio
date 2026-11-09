#!/usr/bin/env python3
"""
Adhi Studio - Phone Export Pipeline Engine
Menyalin output siap posting dari project yang sudah di-render langsung ke HP (MTP/GVFS).
Menyalin HANYA file deliverable final (video .mp4, meme .jpg, caption .txt)
langsung ke folder <dest>/<project_id>/ tanpa subfolder 'output' dan tanpa file intermediate sampah.
"""

import os
import sys
import shutil
import glob
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")

def detect_phone_destination():
    """
    Mendeteksi perangkat HP yang terhubung via GVFS MTP di Linux.
    Mengembalikan dict informasi koneksi & path rekomendasi.
    """
    uid = os.getuid()
    gvfs_dir = f"/run/user/{uid}/gvfs"
    
    last_known_poco = f"/run/user/{uid}/gvfs/mtp:host=Android_Device_MTP/Penyimpanan bersama internal/Documents/konten"
    local_fallback = os.path.join(os.path.dirname(BASE_DIR), "export_siap_posting")

    if not os.path.exists(gvfs_dir):
        return {
            "connected": False,
            "phone_name": "Tidak Terdeteksi",
            "mount_path": None,
            "target_path": last_known_poco,
            "local_fallback": local_fallback,
            "message": "Folder GVFS tidak ditemukan. Pastikan HP terhubung via USB dalam mode 'Transfer File / MTP'."
        }

    try:
        entries = os.listdir(gvfs_dir)
    except Exception as e:
        entries = []

    mtp_mounts = [e for e in entries if e.startswith("mtp:")]
    
    if not mtp_mounts:
        return {
            "connected": False,
            "phone_name": "Belum Terhubung",
            "mount_path": None,
            "target_path": last_known_poco,
            "local_fallback": local_fallback,
            "message": "HP belum tercolok atau belum diatur ke mode 'Transfer File / MTP'."
        }

    # Ambil mount pertama atau yang cocok dengan Android MTP
    chosen_mount = mtp_mounts[0]
    for m in mtp_mounts:
        if "xiaomi" in m.lower() or "poco" in m.lower():
            chosen_mount = m
            break

    mount_path = os.path.join(gvfs_dir, chosen_mount)
    phone_name = chosen_mount.replace("mtp:host=", "").split("_b0cd")[0].replace("_", " ")

    # Cari internal storage
    storage_candidates = [
        "Penyimpanan bersama internal",
        "Internal shared storage",
        "Internal storage",
        "Penyimpanan internal",
        "Shared storage"
    ]
    storage_path = mount_path
    try:
        sub_items = os.listdir(mount_path)
        for s in sub_items:
            if s in storage_candidates or "internal" in s.lower() or "bersama" in s.lower():
                storage_path = os.path.join(mount_path, s)
                break
    except Exception:
        pass

    if storage_path == mount_path:
        storage_path = os.path.join(mount_path, "Penyimpanan bersama internal")

    target_konten = os.path.join(storage_path, "Documents", "konten")

    return {
        "connected": True,
        "phone_name": phone_name,
        "mount_path": mount_path,
        "storage_path": storage_path,
        "target_path": target_konten,
        "local_fallback": local_fallback,
        "message": f"Terdeteksi perangkat: {phone_name}"
    }

def get_rendered_projects():
    """
    Mengambil seluruh project yang sudah memiliki hasil render MP4 di folder output/.
    """
    results = []
    if not os.path.exists(PROJECTS_DIR):
        return results

    project_dirs = sorted(os.listdir(PROJECTS_DIR))
    for p_name in project_dirs:
        p_path = os.path.join(PROJECTS_DIR, p_name)
        if not os.path.isdir(p_path) or p_name.startswith((".", "_")):
            continue

        # Prioritaskan final_output/ (Remake NotebookLM), jika belum ada gunakan output/ lama
        out_dir = os.path.join(p_path, "final_output")
        is_final_output = True
        if not os.path.isdir(out_dir) or not any(f.endswith(".mp4") for f in os.listdir(out_dir)):
            out_dir = os.path.join(p_path, "output")
            is_final_output = False
            if not os.path.isdir(out_dir):
                continue

        try:
            files = os.listdir(out_dir)
        except Exception:
            continue

        # Cek apakah ada file video MP4
        video_files = [f for f in files if f.endswith(".mp4")]
        if not video_files:
            continue

        # Ambil metadata dari project.json jika ada
        title = p_name
        topic = ""
        json_path = os.path.join(p_path, "project.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    pdata = json.load(f)
                    title = pdata.get("title", p_name)
                    topic = pdata.get("topic", "")
            except Exception:
                pass

        # Hitung file deliverable
        deliverables = []
        total_size = 0
        for f in files:
            if f.startswith((".", "preview_")) or f.endswith((".tmp", ".part")):
                continue
            fp = os.path.join(out_dir, f)
            if os.path.isfile(fp):
                sz = os.path.getsize(fp)
                total_size += sz
                deliverables.append({
                    "name": f,
                    "size": sz,
                    "is_video": f.endswith(".mp4"),
                    "is_meme": "_meme_" in f,
                    "is_caption": f.endswith(".txt")
                })

        mtime = os.path.getmtime(out_dir)

        results.append({
            "id": p_name,
            "title": title,
            "topic": topic,
            "has_video": True,
            "files_count": len(deliverables),
            "files": deliverables,
            "size_bytes": total_size,
            "size_mb": round(total_size / (1024 * 1024), 2),
            "modified_time": mtime
        })

    # Urutkan berdasarkan nomor prefix project jika ada
    def sort_key(item):
        m = re.match(r"^(\d+)", item["id"])
        return int(m.group(1)) if m else 9999

    results.sort(key=sort_key)
    return results

def copy_project_output(project_id, destination_dir, overwrite=True):
    """
    Menyalin isi output/ dari 1 project ke <destination_dir>/<project_id>/
    Secara otomatis TIDAK menyalin intermediate files sampah.
    """
    proj_path = os.path.join(PROJECTS_DIR, project_id)
    if not os.path.exists(proj_path):
        raise FileNotFoundError(f"Project '{project_id}' tidak ditemukan di {PROJECTS_DIR}")

    # Cek apakah project menggunakan final_output/ (NotebookLM) atau output/ lama
    out_dir = os.path.join(proj_path, "final_output")
    is_remake = True
    if not os.path.exists(out_dir) or not any(f.endswith(".mp4") for f in os.listdir(out_dir)):
        out_dir = os.path.join(proj_path, "output")
        is_remake = False
        if not os.path.exists(out_dir):
            raise FileNotFoundError(f"Folder output/final_output tidak ditemukan di project '{project_id}'")

    target_dir = os.path.join(destination_dir, project_id)
    os.makedirs(target_dir, exist_ok=True)

    copied_files = []
    total_bytes = 0

    # 1. Salin seluruh file deliverable dari out_dir (final_output atau output)
    for item in os.listdir(out_dir):
        if item.startswith((".", "preview_")) or item.endswith((".tmp", ".part")):
            continue
        # Jika remake, abaikan meme jika ada
        if is_remake and "_meme_" in item:
            continue
        src = os.path.join(out_dir, item)
        dst = os.path.join(target_dir, item)
        if os.path.isfile(src):
            if overwrite or not os.path.exists(dst):
                shutil.copy2(src, dst)
                sz = os.path.getsize(dst)
                total_bytes += sz
                copied_files.append({"name": item, "size": sz})

    # 2. Jika bukan remake (mode lama), cek apakah ada caption/thumbnail tambahan di root
    if not is_remake:
        extra_files = ["thumbnail.jpg"] + glob.glob(os.path.join(proj_path, "caption_*.txt"))
        for ext_path in extra_files:
            if os.path.isfile(ext_path):
                ext_name = os.path.basename(ext_path)
                dst = os.path.join(target_dir, ext_name)
                if not os.path.exists(dst):
                    shutil.copy2(ext_path, dst)
                    sz = os.path.getsize(dst)
                    total_bytes += sz
                    copied_files.append({"name": ext_name, "size": sz})

    return {
        "project_id": project_id,
        "target_dir": target_dir,
        "copied_count": len(copied_files),
        "files": copied_files,
        "total_bytes": total_bytes,
        "total_mb": round(total_bytes / (1024 * 1024), 2)
    }

def export_batch(project_ids, destination_dir, on_progress=None):
    """
    Menyalin sejumlah project ke destination_dir.
    on_progress(current, total, project_id, status_message)
    """
    os.makedirs(destination_dir, exist_ok=True)
    results = []
    total_copied_files = 0
    total_copied_bytes = 0

    total_projs = len(project_ids)
    for idx, pid in enumerate(project_ids, 1):
        if on_progress:
            on_progress(idx, total_projs, pid, f"Menyalin project [{idx}/{total_projs}]: {pid}")

        try:
            res = copy_project_output(pid, destination_dir)
            results.append({"success": True, "data": res})
            total_copied_files += res["copied_count"]
            total_copied_bytes += res["total_bytes"]
        except Exception as e:
            results.append({"success": False, "project_id": pid, "error": str(e)})

    return {
        "success": True,
        "total_projects": total_projs,
        "total_files": total_copied_files,
        "total_bytes": total_copied_bytes,
        "total_mb": round(total_copied_bytes / (1024 * 1024), 2),
        "destination": destination_dir,
        "details": results
    }

if __name__ == "__main__":
    phone = detect_phone_destination()
    print("=== STATUS DETEKSI HP ===")
    print("Connected :", phone["connected"])
    print("Name      :", phone.get("phone_name"))
    print("Target    :", phone.get("target_path"))
    
    rendered = get_rendered_projects()
    print(f"\n=== DAFTAR PROJECT SIAP EXPORT ({len(rendered)}) ===")
    for p in rendered[:5]:
        print(f"• {p['id']}: {p['title']} ({p['files_count']} file, {p['size_mb']} MB)")
    if len(rendered) > 5:
        print(f"  ... dan {len(rendered) - 5} lainnya.")
