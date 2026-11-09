import http.server
import socketserver
import os
import sys
import json
import urllib.parse
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.project_manager import list_projects, get_project, save_project, create_project_template
from engine.renderer import render_project
from engine.tts import generate_all_audio
from engine.ai_generator import (
    create_and_render_new_project,
    generate_script_scenes,
    check_topic_complexity,
    generate_multiplatform_captions
)
from engine.scheduler import load_schedule, add_schedule_item, update_item_status
from engine.exporter import detect_phone_destination, get_rendered_projects, export_batch
from engine.notebooklm_processor import process_notebooklm_video, process_batch

PORT = 5050
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")

class MarshallHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.do_GET()

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/projects/"):
            proj_id = path.replace("/api/projects/", "").strip("/")
            p_dir = os.path.join(PROJECTS_DIR, proj_id)
            if os.path.exists(p_dir):
                import shutil
                shutil.rmtree(p_dir)
                self.send_json({"success": True, "message": f"Project '{proj_id}' berhasil dihapus"})
            else:
                self.send_json({"error": "Project tidak ditemukan"}, 404)
            return
        self.send_json({"error": "Not found"}, 404)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # API: List projects
        if path == "/api/projects":
            self.send_json(list_projects())
            return

        # API: Get schedule
        if path == "/api/schedule":
            self.send_json(load_schedule())
            return

        # API: Exporter status & rendered projects
        if path == "/api/exporter/status":
            self.send_json({
                "phone": detect_phone_destination(),
                "projects": get_rendered_projects()
            })
            return

        # API: Get project details
        if path.startswith("/api/projects/"):
            proj_id = path.replace("/api/projects/", "").strip("/")
            proj = get_project(proj_id)
            if proj:
                self.send_json(proj[0])
            else:
                self.send_json({"error": "Project not found"}, 404)
            return

        # File serving: /media/<project_id>/<subpath>
        if path.startswith("/media/"):
            rel = path[len("/media/"):].lstrip("/")
            filepath = os.path.join(PROJECTS_DIR, rel)
            if os.path.exists(filepath) and os.path.isfile(filepath):
                self.serve_file_with_range(filepath)
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        # Static web files
        if path == "/" or path == "":
            filepath = os.path.join(WEB_DIR, "index.html")
        else:
            filepath = os.path.join(WEB_DIR, path.lstrip("/"))

        if os.path.exists(filepath) and os.path.isfile(filepath):
            self.serve_file(filepath)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # API: Delete project
        if path.startswith("/api/projects/") and path.endswith("/delete"):
            proj_id = path.replace("/api/projects/", "").replace("/delete", "").strip("/")
            p_dir = os.path.join(PROJECTS_DIR, proj_id)
            if os.path.exists(p_dir):
                import shutil
                shutil.rmtree(p_dir)
                self.send_json({"success": True, "message": f"Project '{proj_id}' berhasil dihapus"})
            else:
                self.send_json({"error": "Project tidak ditemukan"}, 404)
            return

        # API: Check topic complexity (Part 1 vs Single)
        if path == "/api/check-complexity":
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
            topic = payload.get("topic", "")
            res = check_topic_complexity(topic)
            self.send_json(res)
            return

        # API: Generate script only (Step 2 Preview & Teleprompter)
        if path == "/api/generate-script-only":
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
            topic = payload.get("topic", "").strip()
            tone = payload.get("tone", "santai")
            part_num = payload.get("part_num")
            total_parts = payload.get("total_parts", 1)
            
            scenes = generate_script_scenes(topic, tone, part_num, total_parts)
            captions = generate_multiplatform_captions(topic, part_num)
            
            # Count total words & estimated speaking duration
            total_words = sum(len(s["text"].split()) for s in scenes)
            est_seconds = int(round(total_words / 2.3)) # ~2.3 words/sec in Indonesian
            
            self.send_json({
                "success": True,
                "scenes": scenes,
                "captions": captions,
                "total_words": total_words,
                "est_seconds": est_seconds
            })
            return

        # API: Generate full video (Step 4 Rendering)
        if path == "/api/generate-full":
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
            topic = payload.get("topic", "").strip()
            tone = payload.get("tone", "santai")
            voice = payload.get("voice", "id-ID-ArdiNeural")
            audio_b64 = payload.get("audio_base64")
            part_num = payload.get("part_num")
            total_parts = payload.get("total_parts", 1)
            custom_scenes = payload.get("scenes")

            if not topic:
                self.send_json({"error": "Topik tidak boleh kosong"}, 400)
                return

            custom_audio_file = None
            if audio_b64:
                import base64
                tmp_dir = os.path.join(PROJECTS_DIR, "_tmp")
                os.makedirs(tmp_dir, exist_ok=True)
                custom_audio_file = os.path.join(tmp_dir, f"voice_{int(time.time())}.mp3")
                with open(custom_audio_file, "wb") as f:
                    f.write(base64.b64decode(audio_b64))

            try:
                pid, pdata, out_video = create_and_render_new_project(
                    topic=topic,
                    tone=tone,
                    voice=voice,
                    custom_audio_file=custom_audio_file,
                    part_num=part_num,
                    total_parts=total_parts,
                    custom_scenes=custom_scenes
                )
                self.send_json({
                    "success": True,
                    "project_id": pid,
                    "project": pdata,
                    "output": out_video,
                    "message": "Video shorts & Social Media Kit berhasil dibuat!"
                })
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, 500)
            return

        # API: Render project
        if path.startswith("/api/render/"):
            proj_id = path.replace("/api/render/", "").strip("/")
            proj = get_project(proj_id)
            if not proj:
                self.send_json({"error": "Project not found"}, 404)
                return

            proj_data, p_dir = proj
            try:
                out = render_project(proj_data, p_dir)
                self.send_json({"success": True, "message": "Video rendered successfully", "output": out})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, 500)
            return

        # API: Upload custom voice and auto-sync
        if path.startswith("/api/upload-voice/"):
            proj_id = path.replace("/api/upload-voice/", "").strip("/")
            proj = get_project(proj_id)
            if not proj:
                self.send_json({"error": "Project not found"}, 404)
                return
            proj_data, p_dir = proj
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
            
            import base64
            audio_bytes = base64.b64decode(payload["audio_base64"])
            ext = payload.get("filename", "voice.mp3").split(".")[-1]
            custom_audio_file = os.path.join(p_dir, "audio", f"custom_voice.{ext}")
            with open(custom_audio_file, "wb") as f:
                f.write(audio_bytes)
            
            out = render_project(proj_data, p_dir, custom_audio_path=custom_audio_file)
            self.send_json({"success": True, "output": out, "message": "Voiceover tersinkronisasi otomatis!"})
            return

        # API: Schedule actions
        if path == "/api/schedule/add":
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
            res = add_schedule_item(
                payload.get("topic", "Topik Baru"),
                payload.get("target_date", "2026-10-07"),
                payload.get("target_time", "20:00 WIB"),
                payload.get("project_id")
            )
            self.send_json({"success": True, "schedule": res})
            return

        if path == "/api/schedule/update-status":
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
            res = update_item_status(payload.get("item_id"), payload.get("status"))
            self.send_json({"success": True, "schedule": res})
            return

        # API: Run 1-Click Export to Phone
        if path == "/api/exporter/run":
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length)) if length > 0 else {}
            project_ids = payload.get("project_ids", [])
            destination = payload.get("destination")
            if not destination:
                phone_info = detect_phone_destination()
                destination = phone_info.get("target_path") or phone_info.get("local_fallback")
            
            try:
                res = export_batch(project_ids, destination)
                self.send_json(res)
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, 500)
            return

        # API: Process NotebookLM video
        if path == "/api/notebooklm/process":
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length)) if length > 0 else {}
            pid = payload.get("project_id")
            bumper = float(payload.get("bumper_cut_seconds", 3.0))
            intro = float(payload.get("intro_seconds", 1.0))
            
            try:
                if pid:
                    res = process_notebooklm_video(pid, bumper_cut_seconds=bumper, intro_seconds=intro)
                else:
                    res = process_batch(bumper_cut_seconds=bumper, intro_seconds=intro)
                self.send_json({"success": True, "result": res})
            except Exception as e:
                self.send_json({"success": False, "error": str(e)}, 500)
            return

        self.send_json({"error": "Not found"}, 404)

    def serve_file(self, filepath):
        content_type = self.guess_mime(filepath)
        with open(filepath, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def serve_file_with_range(self, filepath):
        try:
            content_type = self.guess_mime(filepath)
            file_size = os.path.getsize(filepath)
            range_header = self.headers.get("Range")

            if range_header:
                try:
                    range_match = range_header.strip().lower().replace("bytes=", "")
                    parts = range_match.split("-")
                    start = int(parts[0]) if parts[0] else 0
                    end = int(parts[1]) if parts[1] else file_size - 1
                    length = end - start + 1

                    self.send_response(206)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                    self.send_header("Content-Length", str(length))
                    self.send_header("Accept-Ranges", "bytes")
                    self.end_headers()

                    with open(filepath, "rb") as f:
                        f.seek(start)
                        self.wfile.write(f.read(length))
                    return
                except Exception:
                    pass

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            with open(filepath, "rb") as f:
                self.wfile.write(f.read())
        except (BrokenPipeError, ConnectionResetError):
            pass

    def guess_mime(self, path):
        if path.endswith(".html"): return "text/html"
        if path.endswith(".css"): return "text/css"
        if path.endswith(".js"): return "application/javascript"
        if path.endswith(".json"): return "application/json"
        if path.endswith(".jpg") or path.endswith(".jpeg"): return "image/jpeg"
        if path.endswith(".png"): return "image/png"
        if path.endswith(".mp4"): return "video/mp4"
        if path.endswith(".mp3"): return "audio/mpeg"
        if path.endswith(".vtt"): return "text/vtt"
        return "application/octet-stream"

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), MarshallHandler) as httpd:
        print(f"\n🚀 Adhi Studio running at: http://localhost:{PORT}")
        print("Tekan Ctrl+C untuk berhenti.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer dihentikan.")

if __name__ == "__main__":
    run_server()
