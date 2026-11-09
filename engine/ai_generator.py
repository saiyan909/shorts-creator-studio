import os
import re
import urllib.parse
import urllib.request
import json
import time

from engine.tts import generate_all_audio
from engine.renderer import render_project
from engine.project_manager import save_project
from engine.thumbnail import create_minimalist_thumbnail

def sanitize_id(text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())
    words = cleaned.split()[:4]
    prefix = int(time.time()) % 10000
    return f"{prefix}_{'_'.join(words)}"

def check_topic_complexity(topic: str) -> dict:
    keywords_history = ["sejarah", "asal-usul", "awal mula", "perang", "kronologi", "evolusi", "kerajaan", "dunia"]
    is_complex = any(k in topic.lower() for k in keywords_history) or len(topic.split()) > 10
    return {
        "needs_multi_part": is_complex,
        "recommended_parts": 2 if is_complex else 1,
        "reason": "Topik ini memiliki alur sejarah / penjelasan mendalam. Sangat disarankan dipecah menjadi Part 1 & Part 2 agar durasi tetap padat di bawah 1 menit." if is_complex else "Topik pas untuk format 1 video utuh (~50 detik)."
    }

def load_ai_config():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg_path = os.path.join(base_dir, "config.json")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def call_omniroute_llm(topic: str, tone: str = "santai", part_num: int = None, total_parts: int = 1):
    cfg = load_ai_config()
    omni = cfg.get("omniroute", {})
    base_url = omni.get("base_url", "https://omniroute.marshall-teach.web.id/v1")
    api_key = omni.get("api_key")
    model = omni.get("model", "video-gen")

    if not api_key:
        return None

    part_info = f" (Part {part_num} dari {total_parts})" if total_parts > 1 else ""

    sys_prompt = f"""Kamu adalah AI Scriptwriter profesional kelas dunia untuk channel YouTube Shorts & TikTok 'Teman Overthinking' (@teman_overthinking).
Tugasmu adalah membuat naskah video vertikal 9:16 yang viral, berbobot ilmiah/psikologis mendalam, lucu, dan sangat relate dengan penonton Indonesia.

Ketentuan Naskah:
1. Terdiri tepat dari 5 adegan (Scene 1 s/d Scene 5).
2. TOTAL KATA kelima adegan WAJIB antara 125 sampai 138 kata (durasi 50-54 detik). JANGAN KURANG DARI 120 KATA, JANGAN LEBIH DARI 145 KATA.
3. Scene 1: Hook rasa penasaran menggelitik tentang topik{part_info}.
4. Scene 2: Kontras atau mitos salah kaprah yang sering dipercaya orang.
5. Scene 3: Inti penjelasan ilmiah / psikologis / biologi mendalam yang dibongkar tuntas dengan bahasa santai.
6. Scene 4: Fakta / analogi kehidupan sehari-hari / data mengejutkan yang bikin penonton manggut-manggut ('AHA moment').
7. Scene 5: Penutup bernas dan Call To Action (CTA) yang memancing penonton menulis komentar atau berdebat.
8. PENTING UNTUK SUBTITLES:
   Field 'subtitles' WAJIB memecah narasi dari field 'text' menjadi 3-4 baris potongan kalimat pendek (5-7 kata per baris) PERSIS dengan apa yang diucapkan di 'text'.
   DILARANG KERAS membuat rangkuman singkat atau kalimat berbeda yang tidak diucapkan di narasi!
9. Output WAJIB berupa JSON murni tanpa markdown:
{{
  "scenes": [
    {{
      "id": 1,
      "text": "Pernah perhatiin fenomena misterius ini? Kenapa bapak-bapak kalau mandi pagi cuma butuh 3 menit, tapi giliran buang air besar di toilet bisa betah setengah jam lebih?",
      "prompt": "A 3D Pixar animated style illustration of ..., warm cozy lighting, 9:16 vertical orientation",
      "subtitles": [
        {{"start": 0.1, "end": 2.5, "text": "Pernah perhatiin fenomena misterius ini?", "highlight": false}},
        {{"start": 2.5, "end": 5.5, "text": "Kenapa kalau mandi pagi cuma butuh 3 menit,", "highlight": false}},
        {{"start": 5.5, "end": 8.5, "text": "Tapi giliran BAB betah setengah jam lebih?", "highlight": true}}
      ]
    }}
  ]
}}"""

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"Buat naskah Shorts 5 adegan untuk topik: '{topic}'. Nada: {tone}."}
        ],
        "temperature": 0.7
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
    )

    try:
        print(f"  [AI-ENGINE] Menghubungi OmniRoute Claude ({model}) untuk topik '{topic}'...")
        with urllib.request.urlopen(req, timeout=35) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = data["choices"][0]["message"]["content"].strip()
            clean = re.sub(r"^```json\s*", "", raw, flags=re.I)
            clean = re.sub(r"^```\s*", "", clean)
            clean = re.sub(r"```$", "", clean).strip()
            json_match = re.search(r"\{[\s\S]*\}", clean)
            if json_match:
                parsed = json.loads(json_match.group(0))
                if "scenes" in parsed and len(parsed["scenes"]) == 5:
                    print(f"  [AI-ENGINE] Berhasil generate naskah dari Claude ({model})!")
                    return clean_and_align_subtitles(parsed["scenes"])
    except Exception as e:
        print(f"  [AI-ENGINE Warning] OmniRoute call failed: {e}. Menggunakan engine cadangan...")
    return None

def clean_and_align_subtitles(scenes: list) -> list:
    """Memastikan setiap adegan memiliki subtitle yang 100% cocok dengan kalimat di narasi text, bukan rangkuman acak"""
    for s in scenes:
        text = s.get("text", "").strip()
        subtitles = s.get("subtitles", [])
        
        # Cek apakah subtitles kosong, atau terlalu sedikit (hanya 2 baris rangkuman)
        is_mismatched = False
        if not subtitles or len(subtitles) <= 2:
            is_mismatched = True
        else:
            all_sub_text = " ".join([sub.get("text", "") for sub in subtitles]).lower()
            text_lower = text.lower()
            # Cek apakah teks subtitle benar-benar ada di dalam narasi
            words_in_subs = re.findall(r'\w+', all_sub_text)
            match_count = sum(1 for w in words_in_subs if w in text_lower)
            if match_count < len(words_in_subs) * 0.5:
                is_mismatched = True

        if is_mismatched and text:
            # Pecah kalimat narasi asli secara natural berdasarkan tanda baca
            raw_clauses = re.split(r'([.?!,;]+)', text)
            chunks = []
            for i in range(0, len(raw_clauses), 2):
                cl = raw_clauses[i].strip()
                punct = raw_clauses[i+1] if i+1 < len(raw_clauses) else ""
                full_cl = f"{cl}{punct}".strip()
                if not full_cl:
                    continue
                w_list = full_cl.split()
                if len(w_list) <= 8:
                    chunks.append(full_cl)
                else:
                    half = len(w_list) // 2
                    chunks.append(" ".join(w_list[:half]))
                    chunks.append(" ".join(w_list[half:]))

            new_subs = []
            for idx, c in enumerate(chunks):
                new_subs.append({
                    "start": 0.1,
                    "end": 3.0,
                    "text": c,
                    "highlight": (idx == len(chunks) - 1 or "!" in c or "?" in c)
                })
            s["subtitles"] = new_subs
    return scenes

def generate_script_scenes(topic: str, tone: str = "santai", part_num: int = None, total_parts: int = 1):
    # 1. Coba hubungi OmniRoute (Claude)
    omni_scenes = call_omniroute_llm(topic, tone, part_num, total_parts)
    if omni_scenes:
        return omni_scenes

    part_suffix = f" (Part {part_num}/{total_parts})" if total_parts > 1 else ""
    t_lower = topic.lower()

    # ================= TOPIC 1: BAPAK BAB LAMA VS MANDI CEPAT =================
    if any(k in t_lower for k in ["bapak", "ayah"]) and any(k in t_lower for k in ["pup", "bab", "berak", "toilet", "wc", "kamar mandi", "mandi"]):
        return [
            {
                "id": 1,
                "text": "Pernah merhatiin fenomena ini? Kenapa bapak-bapak kalau mandi pagi cuma butuh tiga menit, tapi giliran buang air besar di toilet bisa betah setengah jam lebih? Ke mana hilangnya waktu itu?",
                "prompt": "A funny expressive 3D Pixar style Indonesian dad standing outside a bathroom looking rushed in the morning vs relaxing peacefully inside, 9:16 vertical orientation",
                "subtitles": [
                    {"start": 0.1, "end": 2.2, "text": "Pernah merhatiin fenomena ini?", "highlight": False},
                    {"start": 2.2, "end": 5.2, "text": "Kenapa bapak-bapak mandi cuma 3 menit...", "highlight": False},
                    {"start": 5.2, "end": 8.5, "text": "Tapi giliran BAB betah setengah jam?", "highlight": True}
                ]
            },
            {
                "id": 2,
                "text": "Secara psikologis, mandi pagi bagi kebanyakan bapak-bapak murni misi kilat: basahin badan, sabunan kilat, handukan, beres! Gak ada ritual bengong karena otak mereka sudah fokus ke rutinitas kerja.",
                "prompt": "A comical fast-motion 3D cartoon scene of an Indonesian father taking a lightning fast 3-minute shower with soap bubbles flying everywhere, clock ticking, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 3.5, "text": "Mandi pagi itu misi kilat bertahan hidup!", "highlight": False},
                    {"start": 3.5, "end": 7.8, "text": "Basahin badan, sabunan, langsung beres!", "highlight": True}
                ]
            },
            {
                "id": 3,
                "text": "Tapi beda cerita pas masuk bilik toilet dan pintu dikunci! Psikolog menyebut fenomena ini sebagai 'micro-sanctuary'. Toilet adalah satu-satunya benteng damai tanpa tuntutan pekerjaan atau anak yang merengek.",
                "prompt": "A peaceful glowing miniature fortress sanctuary concept inside a bathroom, warm golden lighting, peaceful sanctuary vibe, 3D animated style, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 3.2, "text": "Toilet itu 'Micro-Sanctuary'!", "highlight": True},
                    {"start": 3.2, "end": 7.8, "text": "Benteng damai tanpa tuntutan kerja dan anak!", "highlight": False}
                ]
            },
            {
                "id": 4,
                "text": "Faktanya, proses buang airnya sendiri cuma lima menit. Sisanya? Dua puluh menit dipakai buat doom-scrolling nonton video reels mancing, cek grup WhatsApp ronda, atau baca berita sampai kakinya kesemutan!",
                "prompt": "A humorous 3D cartoon dad sitting comfortably in a bathroom toilet scrolling his smartphone screen glowing on his face, funny expressions, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 2.8, "text": "Hajatnya sendiri cuma 5 menit...", "highlight": False},
                    {"start": 2.8, "end": 7.8, "text": "20 menitnya buat doom-scrolling video mancing!", "highlight": True}
                ]
            },
            {
                "id": 5,
                "text": "Jadi toilet itu ruang bertapa paling damai seorang bapak! Menurutmu bapakmu atau kamu sendiri kayak gini juga nggak? Tulis pengakuanmu di kolom komentar ya!",
                "prompt": "A friendly relatable 3D character smiling warmly holding a smartphone pointing to interactive floating comment bubbles, cozy studio lighting, 9:16 vertical ending scene",
                "subtitles": [
                    {"start": 0.1, "end": 3.2, "text": "Ruang bertapa paling damai seorang bapak!", "highlight": False},
                    {"start": 3.2, "end": 6.8, "text": "Bapakmu kayak gini juga nggak? Komen! 👇", "highlight": True}
                ]
            }
        ]

    # ================= TOPIC 2: IDE MUNCUL PAS MANDI =================
    if any(k in t_lower for k in ["mandi", "shower"]) and any(k in t_lower for k in ["ide", "kreatif", "solusi", "brilian", "otak"]):
        return [
            {
                "id": 1,
                "text": "Pernah nggak sih kamu lagi pusing seharian mikirin masalah, tapi pas lagi mandi di bawah guyuran air hangat, tiba-tiba otakmu dapet ide brilian yang jenius banget? Kenapa ide terbaik selalu muncul di kamar mandi?",
                "prompt": "A stylized 3D cartoon person showering under warm water with a glowing golden lightbulb appearing above their head, magical sparks, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 2.5, "text": "Lagi pusing seharian mikirin masalah...", "highlight": False},
                    {"start": 2.5, "end": 6.0, "text": "Tiba-tiba dapet ide brilian pas mandi?", "highlight": True}
                ]
            },
            {
                "id": 2,
                "text": "Fenomena ini bukan hal mistis, tapi murni sains neurobiologi! Saat mandi, kita melakukan aktivitas fisik yang repetitif dan otomatis tanpa perlu fokus tinggi, sehingga otak merasa sangat aman dan tenang.",
                "prompt": "A creative 3D neuroscience illustration of a relaxing brain emitting glowing blue alpha waves, clean medical aesthetic, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 3.5, "text": "Bukan mistis, ini sains neurobiologi!", "highlight": True},
                    {"start": 3.5, "end": 7.5, "text": "Aktivitas monoton bikin otak merasa rileks.", "highlight": False}
                ]
            },
            {
                "id": 3,
                "text": "Kondisi rileks ini memicu otak masuk ke mode gelombang Alpha dan membanjiri sistem saraf dengan hormon Dopamin. Di saat bersamaan, jaringan misterius bernama Default Mode Network atau DMN aktif secara penuh!",
                "prompt": "A dynamic 3D animation of dopamine molecules floating like gold glitter around neural pathways, vibrant cinematic lighting, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 3.2, "text": "Gelombang Alpha & lonjakan Dopamin!", "highlight": True},
                    {"start": 3.2, "end": 7.8, "text": "Default Mode Network otak aktif maksimal!", "highlight": False}
                ]
            },
            {
                "id": 4,
                "text": "DMN inilah yang bertugas menghubungkan memori-memori acak yang selama ini terpisah di alam bawah sadar, lalu merangkainya menjadi sebuah solusi kreatif tak terduga yang bikin kamu kaget sendiri.",
                "prompt": "A 3D cartoon mind puzzle connecting scattered jigsaw pieces into a glowing masterpiece idea, eureka moment, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 3.5, "text": "Menghubungkan memori acak bawah sadar...", "highlight": False},
                    {"start": 3.5, "end": 7.5, "text": "Jadi sebuah solusi kreatif tak terduga!", "highlight": True}
                ]
            },
            {
                "id": 5,
                "text": "Jadi kalau kamu lagi buntu ide, solusinya bukan dipaksa stres di depan laptop, tapi pergilah mandi air hangat! Ide tergila apa yang pernah muncul pas kamu lagi mandi? Cerita di kolom komentar ya!",
                "prompt": "A friendly 3D cartoon character holding a notepad smiling pointing to neon comments icon, warm ambient glow, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 3.2, "text": "Solusinya mandi air hangat, bukan stres!", "highlight": False},
                    {"start": 3.2, "end": 7.0, "text": "Ide apa yang pernah muncul pas kamu mandi? Komen! 👇", "highlight": True}
                ]
            }
        ]

    # ================= TOPIC 3: KECILIN MUSIK PAS PARKIR / CARI ALAMAT =================
    if any(k in t_lower for k in ["volume", "musik", "lagu"]) and any(k in t_lower for k in ["parkir", "mobil", "alamat", "gang", "nyetir"]):
        return [
            {
                "id": 1,
                "text": "Pernah nggak sih kamu refleks langsung ngecilin volume musik mobil pas lagi nyari gang alamat rumah orang atau mau parkir mundur yang sempit? Padahal kan yang lagi nyari jalan itu matamu, bukan telingamu?",
                "prompt": "A funny 3D cartoon driver squinting intensely at a tiny street sign while quickly turning down car stereo volume knob, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 2.5, "text": "Refleks ngecilin volume musik...", "highlight": False},
                    {"start": 2.5, "end": 6.5, "text": "Pas mau parkir atau nyari alamat?", "highlight": True}
                ]
            },
            {
                "id": 2,
                "text": "Ternyata tindakan refleks ini punya penjelasan ilmiah yang sangat cerdas di dunia psikologi kognitif, yaitu yang disebut dengan Cognitive Load Theory atau keterbatasan kapasitas mental otak.",
                "prompt": "A 3D conceptual infographic showing human brain processing capacity meters with bandwidth gauges, neon lighting, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 3.5, "text": "Penjelasan ilmiah: Cognitive Load Theory!", "highlight": True},
                    {"start": 3.5, "end": 7.5, "text": "Otak punya batas bandwidth pemrosesan.", "highlight": False}
                ]
            },
            {
                "id": 3,
                "text": "Saat menyetir santai di jalan lurus, otak kita bekerja santai. Tapi begitu harus membaca nomor rumah kecil atau memperkirakan jarak bumper mobil, korteks visual otak dipaksa bekerja seratus persen!",
                "prompt": "A dynamic 3D split view showing eyes focusing on narrow parking spot while brain computing spatial distance, futuristic HUD, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 3.5, "text": "Korteks visual dipaksa kerja seratus persen!", "highlight": True},
                    {"start": 3.5, "end": 7.5, "text": "Menghitung jarak bumper dan nomor rumah.", "highlight": False}
                ]
            },
            {
                "id": 4,
                "text": "Agar fokus visualmu tidak terpecah, otak secara naluriah memerintahkan tanganmu mematikan input auditori yang bising. Musik keras dianggap 'sampah informasi' yang bisa memperlambat refleks spasialmu.",
                "prompt": "A 3D animated brain cutting off sound wave clutter to boost razor sharp visual focus laser beam, cinematic tech style, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 3.5, "text": "Musik dianggap 'sampah informasi'...", "highlight": False},
                    {"start": 3.5, "end": 7.5, "text": "Otak mematikan suara demi refleks spasial!", "highlight": True}
                ]
            },
            {
                "id": 5,
                "text": "Jadi mengecilkan musik itu bukti otakmu lagi berusaha keras menyelamatkan mobil dari lecet dan nabrak tiang! Kamu tim yang selalu refleks ngecilin volume juga nggak? Tulis di komentar ya!",
                "prompt": "A friendly 3D character winking by a neat parked car pointing to floating comment bubble, warm sunset city street, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 3.2, "text": "Cara cerdas otak nyelametin mobilmu!", "highlight": False},
                    {"start": 3.2, "end": 7.0, "text": "Kamu selalu refleks gini juga nggak? Komen ya! 👇", "highlight": True}
                ]
            }
        ]

    # ================= TOPIC 4: SUARA REKAMAN CEMPRENG =================
    if any(k in t_lower for k in ["suara", "voice note", "vn"]) and any(k in t_lower for k in ["cempreng", "aneh", "rekaman", "rekam"]):
        return [
            {
                "id": 1,
                "text": "Pernah nggak sih kamu denger rekaman suaramu sendiri di voice note WhatsApp dan langsung ngerasa geli atau risih? Kenapa suara di rekaman kedengeran cempreng banget, padahal pas ngomong biasa berasa merdu dan berwibawa?",
                "prompt": "A relatable 3D cartoon young person reacting in funny shock and cringe listening to their phone speaker voice memo, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 2.5, "text": "Denger suara sendiri di voice note...", "highlight": False},
                    {"start": 2.5, "end": 6.5, "text": "Kok kedengeran aneh & cempreng banget?", "highlight": True}
                ]
            },
            {
                "id": 2,
                "text": "Ternyata perbedaan drastis ini terjadi karena ada dua jalur transmisi yang berbeda saat suara masuk ke telingamu: konduksi udara dan konduksi tulang.",
                "prompt": "A 3D educational medical diagram of human skull showing sound vibration traveling through bone vs through ear canal, glowing vectors, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 3.5, "text": "Ada 2 jalur transmisi suara:", "highlight": False},
                    {"start": 3.5, "end": 7.5, "text": "Konduksi Udara vs Konduksi Tulang!", "highlight": True}
                ]
            },
            {
                "id": 3,
                "text": "Mikrofon dan orang lain cuma mendengar suaramu lewat getaran udara. Tapi saat kamu ngomong, getaran pita suaramu juga merambat langsung menembus tulang tengkorak dan jaringan kepala bagian dalam.",
                "prompt": "A 3D stylized vocal cords vibrating and acoustic wave resonance inside the skull, deep warm bass glow, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 3.5, "text": "Suaramu merambat tembus tulang tengkorak!", "highlight": True},
                    {"start": 3.5, "end": 7.5, "text": "Menambah resonansi bass alami di kepalamu.", "highlight": False}
                ]
            },
            {
                "id": 4,
                "text": "Tulang tengkorak manusia secara alami memperkuat frekuensi bass rendah dan meredam nada tinggi, membuat kamu terbiasa mendengar suaramu sendiri jauh lebih berat dan empuk dari yang sebenarnya.",
                "prompt": "A graphic audio frequency spectrum curve showing skull bone amplifying low bass frequencies, sleek 3D studio, 9:16 vertical",
                "subtitles": [
                    {"start": 0.1, "end": 3.5, "text": "Tulang memperkuat nada bass rendah...", "highlight": False},
                    {"start": 3.5, "end": 7.5, "text": "Bikin suaramu terdengar lebih empuk di kepalamu!", "highlight": True}
                ]
            },
            {
                "id": 5,
                "text": "Jadi suara cempreng di rekaman itu sebenarnya adalah suara asli kamu yang didengar orang lain selama ini! Seberapa kaget kamu pertama kali denger suaramu sendiri? Tulis di komentar ya!",
                "prompt": "A smiling 3D character holding microphone pointing to comments neon bubble, warm lighting, 9:16 vertical ending scene",
                "subtitles": [
                    {"start": 0.1, "end": 3.5, "text": "Itulah suara asli kamu di mata dunia!", "highlight": False},
                    {"start": 3.5, "end": 7.0, "text": "Seberapa kaget kamu denger rekamanmu? Komen ya! 👇", "highlight": True}
                ]
            }
        ]

    # ================= GENERAL TOPIC: DYNAMIC CONTEXTUAL SYNTHESIZER =================
    # Clean topic for natural phrasing
    clean_topic = re.sub(r'^(kenapa|mengapa|apa alasan|bagaimana cara)\s+', '', topic, flags=re.I).rstrip('?. ')
    
    return [
        {
            "id": 1,
            "text": f"Pernah nggak sih kamu kepikiran hal aneh yang sering kita lewatin ini? Kenapa {clean_topic}? Kelihatannya sepele, tapi kalau dipikir-pikir makin bikin penasaran kan?",
            "prompt": f"A vibrant relatable 3D cartoon character pondering with an intense curious facial expression about {topic}, dynamic lighting, 9:16 vertical composition",
            "subtitles": [
                {"start": 0.1, "end": 2.5, "text": "Pernah kepikiran hal aneh ini?", "highlight": False},
                {"start": 2.5, "end": 6.8, "text": f"Kenapa {clean_topic}?", "highlight": True}
            ]
        },
        {
            "id": 2,
            "text": f"Banyak orang mengira ini terjadi karena kebetulan atau sugesti semata. Padahal kalau kita bedah lebih dalam, ada hukum sains dan mekanisme tersembunyi yang mengatur semuanya secara presisi.",
            "prompt": f"A creative 3D conceptual infographic visualizing the hidden science behind {clean_topic}, glowing blueprints, clean modern laboratory art, 9:16 vertical",
            "subtitles": [
                {"start": 0.1, "end": 3.5, "text": "Bukan kebetulan atau sugesti semata!", "highlight": True},
                {"start": 3.5, "end": 7.5, "text": "Ada mekanisme tersembunyi yang sangat presisi.", "highlight": False}
            ]
        },
        {
            "id": 3,
            "text": f"Secara biologis dan fisika, tubuh serta lingkungan kita terus bertukar sinyal tanpa kita sadari. Respon alami ini sebenarnya adalah cara adaptasi cerdas untuk menghemat energi dan melindungi diri kita.",
            "prompt": f"A stylish 3D scientific visualization of energy transfer and sensory neural pathways explaining {clean_topic}, sparks of light, 9:16 vertical",
            "subtitles": [
                {"start": 0.1, "end": 3.5, "text": "Respon adaptasi alami tubuh kita!", "highlight": True},
                {"start": 3.5, "end": 7.5, "text": "Menghemat energi & merespons lingkungan sekitar.", "highlight": False}
            ]
        },
        {
            "id": 4,
            "text": f"Bahkan para peneliti menemukan bahwa pola unik ini sudah terbentuk secara evolusioner sejak ribuan tahun lalu, dan sampai hari ini masih bekerja otomatis di kehidupan kita sehari-hari.",
            "prompt": f"A fun humorous 3D cartoon moment contrasting ancient human instincts with modern daily life around {clean_topic}, warm cozy lighting, 9:16 vertical",
            "subtitles": [
                {"start": 0.1, "end": 3.5, "text": "Terbentuk sejak ribuan tahun lalu...", "highlight": False},
                {"start": 3.5, "end": 7.5, "text": "Dan masih bekerja otomatis sampai hari ini!", "highlight": True}
            ]
        },
        {
            "id": 5,
            "text": f"Ternyata hal sesepele ini punya rahasia yang mind-blowing banget ya! Menurutmu kamu sering ngalamin ini juga nggak? Coba tulis pendapat atau ceritamu di kolom komentar ya!",
            "prompt": f"A friendly 3D cartoon character holding a smartphone pointing to interactive floating comment bubbles, neon glow, 9:16 vertical ending scene",
            "subtitles": [
                {"start": 0.1, "end": 3.5, "text": "Punya rahasia yang mind-blowing banget!", "highlight": False},
                {"start": 3.5, "end": 7.0, "text": "Kamu sering ngalamin ini juga? Tulis di komentar! 👇", "highlight": True}
            ]
        }
    ]

def call_omniroute_captions(topic: str, part_num: int = None):
    cfg = load_ai_config()
    omni = cfg.get("omniroute", {})
    base_url = omni.get("base_url", "https://omniroute.marshall-teach.web.id/v1")
    api_key = omni.get("api_key")
    model = omni.get("model", "video-gen")

    if not api_key:
        return None

    part_str = f" Part {part_num}" if part_num else ""
    prompt = f"""Kamu adalah Social Media Specialist profesional untuk channel YouTube Shorts & TikTok 'Teman Overthinking' (@teman_overthinking).
Buat 4 versi caption media sosial untuk topik video: '{topic}{part_str}'.
Format output WAJIB JSON murni tanpa markdown:
{{
  "youtube": "Judul menarik, paragraf pembuka, poin-poin penjelasan sains, ajakan subscribe, hashtags",
  "tiktok": "Hook catchy singkat, 3 poin fakta sains unik, ajakan komen, hashtags #fyp #serunyabelajar",
  "instagram": "Hook estetik, penjelasan singkat, ajakan save dan share ke teman, hashtags",
  "facebook": "Gaya bahasa santun dan ramah untuk komunitas keluarga, ajakan diskusi di komentar"
}}"""

    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw = data["choices"][0]["message"]["content"].strip()
            clean = re.sub(r"^```json\s*", "", raw, flags=re.I)
            clean = re.sub(r"^```\s*", "", clean)
            clean = re.sub(r"```$", "", clean).strip()
            json_match = re.search(r"\{[\s\S]*\}", clean)
            if json_match:
                parsed = json.loads(json_match.group(0))
                if all(k in parsed for k in ["youtube", "tiktok", "instagram", "facebook"]):
                    return parsed
    except Exception:
        pass
    return None

def generate_multiplatform_captions(topic: str, part_num: int = None):
    ai_caps = call_omniroute_captions(topic, part_num)
    if ai_caps:
        return ai_caps

    part_str = f" [Part {part_num}]" if part_num else ""
    words = re.findall(r'\b\w+\b', topic.lower())
    clean_topic_tags = [f"#{w}" for w in words if len(w) > 3][:3]
    custom_tags = " ".join(clean_topic_tags) if clean_topic_tags else "#faktamenarik"

    yt_caption = f"""{topic}{part_str} — Fakta Ilmiah & Penjelasan Lengkap 🧠💡

Pernahkah kamu bertanya-tanya kenapa fenomena ini selalu terjadi di sekitar kita? Di video singkat ini kita bongkar alasan psikologis dan sains di baliknya yang jarang disadari orang!

📌 Poin Menarik Pembahasan:
• Penjelasan ilmiah dan mekanisme tersembunyi di balik fenomena ini
• Alasan kenapa tubuh dan pikiran kita merespons secara otomatis
• Fakta unik yang relatable banget sama kehidupan sehari-hari

Kalian tim yang sering ngalamin hal ini atau baru tahu rahasianya sekarang? Tulis cerita atau pendapat kalian di kolom komentar ya! Jangan lupa Like dan Subscribe @teman_overthinking untuk fakta sains seru lainnya!

#Shorts #FaktaSains #Edukasi #SainsUnik #TemanOverthinking #PengetahuanPopuler {custom_tags}"""

    tt_caption = f"""Pernah kepikiran gak sih kenapa hal ini bisa terjadi? 🤔 Rasanya sepele tapi pas tahu faktanya malah mind-blowing!

Rangkuman fakta sainsnya:
• Bukan kebetulan, ada mekanisme biologis dan psikologisnya
• Tubuh dan otak kita merespons sinyal ini secara otomatis
• Relatable banget sama kebiasaan sehari-hari!

Kalian sering ngalamin ini juga gak? Spill pengakuan kalian di kolom komentar ya! 👇

#serunyabelajar #faktaunik #sains #kenapa #temanoverthinking #fyp {custom_tags}"""

    ig_caption = f"""Satu lagi misteri overthinking yang akhirnya terjawab tuntas! 💡🧠

Ternyata kebiasaan ini bukan cuma sugesti atau hal acak, tapi ada penjelasan ilmiah di baliknya. Saat kita tahu alasannya, semuanya jadi masuk akal!

📌 Save reels ini biar gak lupa, dan Share ke temen atau keluarga kamu yang sering ngelakuin hal ini!

Kalian tim yang relate banget atau baru paham sekarang nih? Tulis di komentar ya! 👇

#faktaunik #edukasi #belajardimedsos #sainsindonesia #reelsindonesia #temanoverthinking {custom_tags}"""

    fb_caption = f"""Pernahkah bapak/ibu dan sahabat sekalian bertanya-tanya kenapa hal ini sering sekali terjadi di kehidupan sehari-hari? 🤔

Ternyata ini bukan sekadar kebiasaan biasa, melainkan respon alami tubuh dan psikologi yang punya penjelasan ilmiah menarik.

Semoga wawasan singkat ini bermanfaat ya! Bagaimana dengan pengalaman Anda atau keluarga, apakah sering mengalami hal serupa? Mari kita diskusikan santai di kolom komentar di bawah! 👇

#FaktaMenarik #EdukasiKeluarga #Wawasan #SainsPopuler #TemanOverthinking"""

    return {
        "youtube": yt_caption.strip(),
        "tiktok": tt_caption.strip(),
        "instagram": ig_caption.strip(),
        "facebook": fb_caption.strip()
    }

def download_image(prompt: str, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    import random
    seed = random.randint(10000, 999999)
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?seed={seed}&width=768&height=1344"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://pollinations.ai/"
    })
    success = False
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = resp.read()
            if len(data) > 3000:
                with open(output_path, "wb") as f:
                    f.write(data)
                # Auto-crop bottom 55 pixels to remove any logo/watermark cleanly
                try:
                    from PIL import Image
                    im = Image.open(output_path)
                    w, h = im.size
                    im_clean = im.crop((0, 0, w, h - 55)).resize((w, h), Image.Resampling.LANCZOS)
                    im_clean.save(output_path, quality=95)
                except Exception as e_pil:
                    print(f"PIL watermark clean error: {e_pil}")
                success = True
    except Exception as e:
        print(f"Image generation notice ({e}), mengunduh visual alternatif...")

    # Fallback ke picsum high-res stream jika terkena limit atau gagal, bukan kotak kosong!
    if not success or not os.path.exists(output_path) or os.path.getsize(output_path) < 3000:
        fallback_url = f"https://picsum.photos/seed/{seed}/768/1344"
        try:
            req_fb = urllib.request.Request(fallback_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_fb, timeout=10) as resp_fb, open(output_path, "wb") as f:
                f.write(resp_fb.read())
                print(f"Visual alternatif berhasil dipasang untuk: {output_path}")
        except Exception as e_fb:
            print(f"Fallback warning: {e_fb}")

def create_and_render_new_project(topic: str, tone: str = "santai", voice: str = "id-ID-ArdiNeural", custom_audio_file: str = None, part_num: int = None, total_parts: int = 1, custom_scenes: list = None, progress_cb=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    projects_dir = os.path.join(base_dir, "projects")
    
    project_id = sanitize_id(topic)
    if part_num:
        project_id = f"{project_id}_part{part_num}"

    project_dir = os.path.join(projects_dir, project_id)
    os.makedirs(os.path.join(project_dir, "assets"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "audio"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "output"), exist_ok=True)

    # 1. Naskah
    if custom_scenes:
        scenes_raw = custom_scenes
    else:
        scenes_raw = generate_script_scenes(topic, tone, part_num, total_parts)

    # 2. Thumbnail Minimalis "KENAPA"
    thumb_path = os.path.join(project_dir, "thumbnail.jpg")
    try:
        create_minimalist_thumbnail(topic, thumb_path, part_num=part_num)
    except Exception as e:
        print(f"Thumbnail error: {e}")

    # 3. Generate Visual Assets
    scenes_data = []
    for s in scenes_raw:
        img_filename = f"scene{s['id']}.jpg"
        img_path = os.path.join(project_dir, "assets", img_filename)
        if not os.path.exists(img_path):
            prompt = s.get("prompt", f"3D cartoon scene for {topic}, 9:16 vertical")
            try:
                download_image(prompt, img_path)
            except Exception as e:
                print(f"Image error: {e}")

        scenes_data.append({
            "id": s["id"],
            "text": s["text"],
            "image": f"assets/{img_filename}",
            "audio": f"audio/scene{s['id']}.mp3",
            "subtitles": s.get("subtitles", [])
        })

    # 4. Multi-Platform Social Media Captions
    social_captions = generate_multiplatform_captions(topic, part_num)
    with open(os.path.join(project_dir, "caption_youtube.txt"), "w", encoding="utf-8") as f:
        f.write(social_captions["youtube"])
    with open(os.path.join(project_dir, "caption_tiktok.txt"), "w", encoding="utf-8") as f:
        f.write(social_captions["tiktok"])
    with open(os.path.join(project_dir, "caption_instagram.txt"), "w", encoding="utf-8") as f:
        f.write(social_captions["instagram"])
    with open(os.path.join(project_dir, "caption_facebook.txt"), "w", encoding="utf-8") as f:
        f.write(social_captions["facebook"])

    project_data = {
        "id": project_id,
        "title": topic + (f" (Part {part_num})" if part_num else ""),
        "topic": topic,
        "part_num": part_num,
        "total_parts": total_parts,
        "voice": voice,
        "voice_rate": "+5%",
        "has_thumbnail": os.path.exists(thumb_path),
        "social_kit": social_captions,
        "subtitle_style": {
            "font_name": "Arial Black",
            "font_size": 52,
            "primary_color": "&H00FFFFFF",
            "highlight_color": "&H0000E5FF",
            "outline_color": "&H00000000",
            "outline_width": 5,
            "margin_v": 430
        },
        "scenes": scenes_data
    }

    save_project(project_id, project_data)

    # 5. Audio & Video Render
    if custom_audio_file and os.path.exists(custom_audio_file):
        out_video = render_project(project_data, project_dir, custom_audio_path=custom_audio_file)
    else:
        generate_all_audio(project_data, project_dir)
        out_video = render_project(project_data, project_dir)

    return project_id, project_data, out_video
