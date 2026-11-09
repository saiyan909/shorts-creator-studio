import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")

def list_projects():
    if not os.path.exists(PROJECTS_DIR):
        return []
    projects = []
    for item in sorted(os.listdir(PROJECTS_DIR)):
        p_dir = os.path.join(PROJECTS_DIR, item)
        p_json = os.path.join(p_dir, "project.json")
        if os.path.isdir(p_dir) and os.path.exists(p_json):
            try:
                with open(p_json, "r") as f:
                    data = json.load(f)
                    final_dir = os.path.join(p_dir, "final_output")
                    nlm_dir = os.path.join(p_dir, "notebooklm")
                    
                    has_remake_video = os.path.exists(final_dir) and any(f.endswith(".mp4") for f in os.listdir(final_dir))
                    has_legacy_video = os.path.exists(os.path.join(p_dir, "output", "final_shorts.mp4"))
                    has_nlm_raw = os.path.exists(nlm_dir) and any(f.endswith(".mp4") for f in os.listdir(nlm_dir))
                    
                    projects.append({
                        "id": item,
                        "title": data.get("title", item),
                        "topic": data.get("topic", ""),
                        "scenes_count": len(data.get("scenes", [])),
                        "has_video": has_remake_video or has_legacy_video,
                        "has_remake_video": has_remake_video,
                        "has_nlm_raw": has_nlm_raw,
                        "path": p_dir
                    })
            except Exception as e:
                print(f"Error loading {item}: {e}")
    return projects

def get_project(project_id: str):
    p_dir = os.path.join(PROJECTS_DIR, project_id)
    p_json = os.path.join(p_dir, "project.json")
    if not os.path.exists(p_json):
        return None
    with open(p_json, "r") as f:
        data = json.load(f)
    return data, p_dir

def save_project(project_id: str, data: dict):
    p_dir = os.path.join(PROJECTS_DIR, project_id)
    os.makedirs(p_dir, exist_ok=True)
    p_json = os.path.join(p_dir, "project.json")
    with open(p_json, "w") as f:
        json.dump(data, f, indent=2)

def create_project_template(project_id: str, title: str, topic: str):
    p_dir = os.path.join(PROJECTS_DIR, project_id)
    os.makedirs(os.path.join(p_dir, "assets"), exist_ok=True)
    os.makedirs(os.path.join(p_dir, "audio"), exist_ok=True)
    os.makedirs(os.path.join(p_dir, "output"), exist_ok=True)
    
    template = {
        "id": project_id,
        "title": title,
        "topic": topic,
        "voice": "id-ID-ArdiNeural",
        "voice_rate": "+5%",
        "subtitle_style": {
            "font_name": "Arial Black",
            "font_size": 52,
            "primary_color": "&H00FFFFFF",
            "highlight_color": "&H0000E5FF",
            "outline_color": "&H00000000",
            "outline_width": 5,
            "margin_v": 430
        },
        "scenes": [
            {
                "id": 1,
                "text": "Hook 0-3 detik untuk menarik perhatian penonton...",
                "image": "assets/scene1.jpg",
                "audio": "audio/scene1.mp3",
                "subtitles": [
                    {"start": 0.1, "end": 3.0, "text": "Hook pertanyaan overthinking kamu...", "highlight": true}
                ]
            }
        ]
    }
    save_project(project_id, template)
    return template, p_dir
