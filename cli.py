#!/usr/bin/env python3
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.project_manager import list_projects, get_project, create_project_template
from engine.tts import generate_all_audio
from engine.renderer import render_project

def main():
    parser = argparse.ArgumentParser(description="Marshall Project CLI - Generator Video Shorts")
    subparsers = parser.add_subparsers(dest="command", help="Perintah yang tersedia")

    # Command: list
    subparsers.add_parser("list", help="Tampilkan semua project video")

    # Command: render
    render_parser = subparsers.add_parser("render", help="Render video project menjadi MP4")
    render_parser.add_argument("project_id", help="ID project (contoh: 01_es_tumbler_dingin)")
    render_parser.add_argument("--tts", action="store_true", help="Generate ulang voiceover TTS sebelum render")

    # Command: swap-voice
    swap_parser = subparsers.add_parser("swap-voice", help="Ganti audio dengan file rekaman suara sendiri")
    swap_parser.add_argument("project_id", help="ID project")
    swap_parser.add_argument("audio_path", help="Path file audio (.mp3 / .wav / .m4a)")

    # Command: new
    new_parser = subparsers.add_parser("new", help="Buat template project baru")
    new_parser.add_argument("project_id", help="ID project baru (contoh: 02_overthinking_mandi)")
    new_parser.add_argument("--title", default="Judul Konten", help="Judul konten")
    new_parser.add_argument("--topic", default="Topik Sains/Overthinking", help="Topik pembahasan")

    # Command: ui
    subparsers.add_parser("ui", help="Jalankan Web Studio Dashboard")

    args = parser.parse_args()

    if args.command == "list":
        projects = list_projects()
        print("\n=======================================================")
        print("          MARSHALL PROJECT - DAFTAR KONTEN SHORTS      ")
        print("=======================================================")
        if not projects:
            print("Belum ada project yang dibuat.")
            return
        for p in projects:
            status = "✅ SIAP TONTON" if p["has_video"] else "⏳ BELUM DI-RENDER"
            print(f"• ID       : {p['id']}")
            print(f"  Judul    : {p['title']}")
            print(f"  Topik    : {p['topic']}")
            print(f"  Adegan   : {p['scenes_count']} scene")
            print(f"  Status   : {status}")
            print("-------------------------------------------------------")

    elif args.command == "render":
        proj_data, p_dir = get_project(args.project_id)
        if not proj_data:
            print(f"❌ Project '{args.project_id}' tidak ditemukan!")
            return
        print(f"\n🎬 Memulai render untuk project: {proj_data.get('title')}")
        if args.tts:
            print("🎙️ Menghasilkan audio TTS...")
            generate_all_audio(proj_data, p_dir)
        out = render_project(proj_data, p_dir)
        print(f"\n🎉 Berhasil! Video MP4 tersimpan di:\n👉 {out}\n")

    elif args.command == "swap-voice":
        proj_data, p_dir = get_project(args.project_id)
        if not proj_data:
            print(f"❌ Project '{args.project_id}' tidak ditemukan!")
            return
        if not os.path.exists(args.audio_path):
            print(f"❌ File audio '{args.audio_path}' tidak ditemukan!")
            return
        print(f"\n🎙️ Mengganti audio dengan suara rekaman: {args.audio_path}")
        out = render_project(proj_data, p_dir, custom_audio_path=os.path.abspath(args.audio_path))
        print(f"\n🎉 Berhasil! Video baru dengan suara aslimu tersimpan di:\n👉 {out}\n")

    elif args.command == "new":
        template, p_dir = create_project_template(args.project_id, args.title, args.topic)
        print(f"✅ Template project baru berhasil dibuat di:")
        print(f"👉 {p_dir}")

    elif args.command == "ui":
        os.system(f"python3 {os.path.join(os.path.dirname(__file__), 'server.py')}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
