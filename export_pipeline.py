#!/usr/bin/env python3
"""
Adhi Studio - 1-Click Export to Phone Pipeline
Script 1-klik untuk menyalin file final (video, meme, caption) dari project yang sudah di-render ke HP.
Dapat dijalankan via GUI Zenity (Dialog Desktop) atau CLI Terminal interaktif / otomatis.
"""

import os
import sys
import argparse
import subprocess
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine.exporter import detect_phone_destination, get_rendered_projects, export_batch

def run_zenity_gui():
    """Menjalankan interface 1-klik via Zenity di Desktop Linux."""
    phone = detect_phone_destination()
    rendered = get_rendered_projects()

    if not rendered:
        subprocess.run([
            "zenity", "--warning",
            "--title=Adhi Studio - Export ke HP",
            "--text=Belum ada project yang selesai di-render di folder projects/!\nSilakan render minimal 1 project terlebih dahulu.",
            "--width=400"
        ])
        return

    # 1. Tentukan Default Destination
    default_dest = phone.get("target_path")
    if not phone["connected"]:
        # Tanyakan ke user apakah ingin pakai path HP terakhir atau folder lokal
        choice = subprocess.run([
            "zenity", "--question",
            "--title=Status Sambungan HP",
            "--text=HP Android (MTP) belum terdeteksi aktif di GVFS MTP.\n\nApakah HP sudah dicolok via USB dan diatur ke mode 'Transfer File'?\n\n• Klik 'Ya' jika ingin tetap kirim ke path MTP HP.\n• Klik 'Tidak' jika ingin simpan ke folder lokal komputer.",
            "--ok-label=Kirim ke HP",
            "--cancel-label=Pilih Folder Lokal",
            "--width=450"
        ]).returncode

        if choice != 0:
            default_dest = phone.get("local_fallback")

    # 2. Checklist Pilihan Project via Zenity
    zenity_args = [
        "zenity", "--list", "--checklist",
        "--title=Adhi Studio - Pilih Project Siap Posting",
        "--text=Pilih project yang ingin disalin ke HP (Hanya video & materi posting yang disalin):",
        "--column=Pilih", "--column=ID Project", "--column=Judul", "--column=Ukuran",
        "--width=750", "--height=450", "--separator=|"
    ]

    for p in rendered:
        # Default checked jika project baru (misal ID >= 18)
        checked = "TRUE" if any(p["id"].startswith(f"{i:02d}_") for i in range(18, 55)) else "FALSE"
        zenity_args.extend([checked, p["id"], p["title"][:45], f"{p['size_mb']} MB"])

    sel_res = subprocess.run(zenity_args, capture_output=True, text=True)
    if sel_res.returncode != 0 or not sel_res.stdout.strip():
        print("Export dibatalkan oleh pengguna.")
        return

    selected_ids = [pid.strip() for pid in sel_res.stdout.strip().split("|") if pid.strip()]
    if not selected_ids:
        return

    # 3. Konfirmasi / Ubah Lokasi Output Folder
    dest_res = subprocess.run([
        "zenity", "--entry",
        "--title=Lokasi Folder Tujuan (HP / Staging)",
        f"--text=Tentukan folder tujuan pengiriman ({len(selected_ids)} project dipilih):",
        f"--entry-text={default_dest}",
        "--width=700"
    ], capture_output=True, text=True)

    if dest_res.returncode != 0 or not dest_res.stdout.strip():
        print("Export dibatalkan.")
        return

    final_dest = dest_res.stdout.strip()

    # 4. Eksekusi dengan Progress Bar Zenity
    progress_proc = subprocess.Popen(
        ["zenity", "--progress", "--title=Menyalin ke HP...", f"--text=Menyiapkan pengiriman...", "--percentage=0", "--auto-close", "--width=500"],
        stdin=subprocess.PIPE,
        text=True
    )

    def on_prog(cur, total, pid, msg):
        pct = int((cur / total) * 100)
        try:
            progress_proc.stdin.write(f"{pct}\n")
            progress_proc.stdin.write(f"# [{cur}/{total}] Menyalin: {pid}\n")
            progress_proc.stdin.flush()
        except Exception:
            pass

    report = export_batch(selected_ids, final_dest, on_progress=on_prog)
    try:
        progress_proc.stdin.close()
        progress_proc.wait()
    except Exception:
        pass

    # 5. Notifikasi Selesai
    subprocess.run([
        "zenity", "--info",
        "--title=Export Berhasil! 🎉",
        f"--text=Berhasil menyalin {report['total_projects']} project ({report['total_files']} file / {report['total_mb']} MB) ke:\n\n{final_dest}\n\nFolder sudah bersih dan siap diposting langsung dari galeri HP!",
        "--width=550"
    ])

def run_cli_interactive():
    """Menjalankan interface interaktif di CLI terminal."""
    phone = detect_phone_destination()
    rendered = get_rendered_projects()

    print("\n=======================================================")
    print("   📱 ADHI STUDIO: PIPELINE 1-KLIK COPY KE HP          ")
    print("=======================================================")
    
    if phone["connected"]:
        print(f"🟢 HP Terhubung : {phone['phone_name']}")
        print(f"📁 Target HP    : {phone['target_path']}")
        default_dest = phone["target_path"]
    else:
        print("⚠️  HP Belum Terhubung via USB (MTP).")
        print(f"📁 Target Default HP : {phone['target_path']}")
        print(f"📁 Alternatif Lokal  : {phone['local_fallback']}")
        default_dest = phone["target_path"]

    print("-------------------------------------------------------")
    print(f"Total project yang sudah di-render: {len(rendered)}")
    print("-------------------------------------------------------")
    
    for idx, p in enumerate(rendered, 1):
        print(f"[{idx:2d}] {p['id']} - {p['title'][:40]} ({p['size_mb']} MB)")

    print("\nPilihan Input:")
    print("  - Ketik 'all' untuk pilih semua project")
    print("  - Ketik nomor urut (contoh: 1,3,5) atau ID (contoh: 21,22)")
    print("  - Ketik rentang (contoh: 18-30)")
    
    choice = input("\n👉 Masukkan pilihan project: ").strip()
    if not choice:
        print("❌ Dibatalkan.")
        return

    selected_ids = []
    if choice.lower() == "all":
        selected_ids = [p["id"] for p in rendered]
    elif "-" in choice and choice.replace("-", "").isdigit():
        parts = choice.split("-")
        start, end = int(parts[0]), int(parts[1])
        for p in rendered:
            num = int(p["id"].split("_")[0]) if p["id"].split("_")[0].isdigit() else -1
            if start <= num <= end:
                selected_ids.append(p["id"])
    else:
        items = [x.strip() for x in choice.split(",") if x.strip()]
        for it in items:
            if it.isdigit():
                # cek apakah nomor urut atau nomor project
                idx_num = int(it)
                if 1 <= idx_num <= len(rendered):
                    selected_ids.append(rendered[idx_num - 1]["id"])
                else:
                    for p in rendered:
                        if p["id"].startswith(f"{it:0>2}_") or p["id"].startswith(f"{it}_"):
                            selected_ids.append(p["id"])
            else:
                for p in rendered:
                    if it.lower() in p["id"].lower():
                        selected_ids.append(p["id"])

    # Hapus duplikat
    selected_ids = list(dict.fromkeys(selected_ids))
    if not selected_ids:
        print("❌ Tidak ada project yang cocok dengan pilihanmu.")
        return

    print(f"\n✅ {len(selected_ids)} project dipilih:")
    for sid in selected_ids[:5]:
        print(f"   • {sid}")
    if len(selected_ids) > 5:
        print(f"   ... dan {len(selected_ids) - 5} project lainnya.")

    print(f"\nFolder Tujuan Default:\n👉 {default_dest}")
    custom_dest = input("Tekan [Enter] untuk menggunakan default, atau ketik path lain: ").strip()
    dest_path = custom_dest if custom_dest else default_dest

    print(f"\n🚀 Memulai proses pengiriman ke: {dest_path} ...")
    
    def on_prog(cur, total, pid, msg):
        print(f"[{cur}/{total}] Menyalin {pid}...")

    report = export_batch(selected_ids, dest_path, on_progress=on_prog)
    
    print("\n=======================================================")
    print("🎉 SELESAI! PENGIRIMAN BERHASIL!")
    print(f"• Total Project : {report['total_projects']}")
    print(f"• Total File    : {report['total_files']} file")
    print(f"• Total Ukuran  : {report['total_mb']} MB")
    print(f"• Lokasi Target : {report['destination']}")
    print("=======================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Adhi Studio - 1-Click Copy ke HP")
    parser.add_argument("--projects", help="Daftar project ID (koma terpisah) atau 'all'")
    parser.add_argument("--dest", help="Path folder tujuan di HP / komputer")
    parser.add_argument("--list", action="store_true", help="Tampilkan status HP dan daftar project siap kirim")
    parser.add_argument("--gui", action="store_true", help="Paksa buka mode GUI Zenity")
    parser.add_argument("--cli", action="store_true", help="Paksa buka mode CLI Interaktif")

    args = parser.parse_args()

    if args.list:
        phone = detect_phone_destination()
        rendered = get_rendered_projects()
        print(f"Status HP   : {'TERHUBUNG (' + phone['phone_name'] + ')' if phone['connected'] else 'BELUM TERHUBUNG'}")
        print(f"Target HP   : {phone['target_path']}")
        print(f"Siap Export : {len(rendered)} project")
        for p in rendered:
            print(f"  • {p['id']}: {p['title']} ({p['files_count']} files, {p['size_mb']} MB)")
        return

    # Non-interactive CLI jika parameter diberikan
    if args.projects:
        rendered = get_rendered_projects()
        all_ids = [p["id"] for p in rendered]
        if args.projects.lower() == "all":
            sel_ids = all_ids
        else:
            targets = [x.strip() for x in args.projects.split(",")]
            sel_ids = []
            for t in targets:
                for aid in all_ids:
                    if aid == t or aid.startswith(f"{t}_") or aid.startswith(f"{int(t):02d}_" if t.isdigit() else "___"):
                        sel_ids.append(aid)
            sel_ids = list(dict.fromkeys(sel_ids))

        dest = args.dest
        if not dest:
            phone = detect_phone_destination()
            dest = phone["target_path"]

        print(f"Menyalin {len(sel_ids)} project ke: {dest}")
        res = export_batch(sel_ids, dest, on_progress=lambda c, t, p, m: print(f"[{c}/{t}] {p}"))
        print(f"Selesai! {res['total_files']} file ({res['total_mb']} MB) disalin.")
        return

    # Jika dipanggil manual tanpa argumen:
    # Prioritaskan GUI jika ada tampilan desktop dan Zenity
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    has_zenity = shutil.which("zenity") is not None

    if (has_display and has_zenity and not args.cli) or args.gui:
        try:
            run_zenity_gui()
            return
        except Exception as e:
            print(f"Gagal membuka Zenity GUI ({e}), beralih ke mode CLI.")

    run_cli_interactive()

if __name__ == "__main__":
    main()
