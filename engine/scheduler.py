import os
import json
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEDULE_FILE = os.path.join(BASE_DIR, "schedule.json")

PRIME_TIME_SLOTS = [
    {
        "slot": "Siang (12:00 - 13:00 WIB)",
        "time": "12:00",
        "desc": "Jam istirahat makan siang, orang santai scroll video pendek di kantor / kampus."
    },
    {
        "slot": "Sore (16:30 - 17:30 WIB)",
        "time": "17:00",
        "desc": "Jam perjalanan pulang kerja/sekolah, traffic mulai naik pesat."
    },
    {
        "slot": "Malam (19:30 - 21:00 WIB)",
        "time": "20:00",
        "desc": "THE ULTIMATE PRIME TIME! Saat orang rebahan dan mulai overthinking sebelum tidur."
    }
]

def load_schedule():
    if not os.path.exists(SCHEDULE_FILE):
        initial = {
            "prime_times": PRIME_TIME_SLOTS,
            "items": [
                {
                    "id": "item_1",
                    "project_id": "01_es_tumbler_dingin",
                    "topic": "Kenapa Es di Tumbler Nggak Mencair Seharian?",
                    "target_date": datetime.now().strftime("%Y-%m-%d"),
                    "target_time": "20:00 WIB",
                    "slot_label": "Slot Malam (Overthinking Time)",
                    "status": "ready_to_post", # draft, recording, ready_to_post, posted
                    "platforms": ["YouTube Shorts", "TikTok", "Instagram Reels", "Facebook Reels"]
                }
            ]
        }
        save_schedule(initial)
        return initial
    try:
        with open(SCHEDULE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"prime_times": PRIME_TIME_SLOTS, "items": []}

def save_schedule(data):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_schedule_item(topic: str, target_date: str, target_time: str, project_id: str = None):
    data = load_schedule()
    item_id = f"item_{int(datetime.now().timestamp())}"
    data["items"].append({
        "id": item_id,
        "project_id": project_id,
        "topic": topic,
        "target_date": target_date,
        "target_time": target_time,
        "slot_label": "Jadwal Terencana",
        "status": "planned" if not project_id else "ready_to_post",
        "platforms": ["YouTube Shorts", "TikTok", "Instagram Reels", "Facebook Reels"]
    })
    save_schedule(data)
    return data

def update_item_status(item_id: str, new_status: str):
    data = load_schedule()
    for it in data.get("items", []):
        if it["id"] == item_id:
            it["status"] = new_status
            break
    save_schedule(data)
    return data
