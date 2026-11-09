import os
import textwrap
import urllib.parse
import urllib.request
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "assets", "meme_templates")

# Master URL template meme internet legendaris
TEMPLATE_URLS = {
    "woman_cat": "https://i.imgflip.com/345v97.jpg",
    "disaster_girl": "https://i.imgflip.com/23ls.jpg",
    "drake": "https://i.imgflip.com/30b1gx.jpg",
    "spongebob": "https://i.imgflip.com/1otk96.jpg",
    "doge_cheems": "https://i.imgflip.com/43a45p.png",
    "uno_25": "https://i.imgflip.com/3lmzyx.jpg",
    "pablo": "https://i.imgflip.com/1c1uej.jpg",
    "two_buttons": "https://i.imgflip.com/1g8my4.jpg",
    "trade_offer": "https://i.imgflip.com/54hjww.jpg",
    "distracted_bf": "https://i.imgflip.com/1ur9b0.jpg",
    "clown": "https://i.imgflip.com/38el31.jpg",
    "side_eye": "https://i.imgflip.com/261o3j.jpg",
    "waiting_skeleton": "https://i.imgflip.com/2fm6x.jpg"
}

def get_meme_font(size: int = 54):
    font_paths = [
        os.path.join(BASE_DIR, "assets", "fonts", "Montserrat-Black.ttf"),
        os.path.join(BASE_DIR, "assets", "fonts", "Poppins-Black.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

def ensure_template_exists(template_name: str) -> str:
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    local_path = os.path.join(TEMPLATES_DIR, f"{template_name}.jpg")
    if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
        return local_path

    url = TEMPLATE_URLS.get(template_name, "https://i.imgflip.com/1c1uej.jpg")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as r, open(local_path, "wb") as f:
            f.write(r.read())
        print(f"  [MEME-TEMPLATE] Berhasil mengunduh template: {template_name}")
    except Exception as e:
        print(f"  [MEME-TEMPLATE Warning] Gagal mengunduh {template_name}: {e}")
    return local_path

def create_pure_meme_image(
    template_name: str,
    top_text: str,
    bottom_text: str,
    output_path: str
):
    """
    Format Pure Meme Asli (Standar Resmi Instagram Portrait 4:5 = 1080x1350):
    - 100% pas dengan standar Feed/Carousel Instagram tanpa kena warning auto-crop
    - Background ambient blur dari gambar meme
    - Template meme tajam di tengah
    - Punchline ATAS dan BAWAH tebal putih stroke hitam
    """
    canvas_w, canvas_h = 1080, 1350
    font = get_meme_font(48)

    tpl_path = ensure_template_exists(template_name)
    if os.path.exists(tpl_path):
        meme_raw = Image.open(tpl_path).convert("RGB")
    else:
        meme_raw = Image.new("RGB", (800, 600), (30, 41, 59))

    mw, mh = meme_raw.size

    # 1. Background full canvas 4:5
    bg_scaled = meme_raw.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
    bg_blurred = bg_scaled.filter(ImageFilter.GaussianBlur(35))
    dim = Image.new("RGB", (canvas_w, canvas_h), (0, 0, 0))
    bg = Image.blend(bg_blurred, dim, 0.42)

    # 2. Foreground meme: full width (1080px)
    fg_w = canvas_w
    fg_h = int(mh * (fg_w / mw))
    if fg_h > 840:
        fg_h = 840
        fg_w = int(mw * (fg_h / mh))

    fg_meme = meme_raw.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
    y_fg = (canvas_h - fg_h) // 2
    x_fg = (canvas_w - fg_w) // 2
    bg.paste(fg_meme, (x_fg, y_fg))

    draw = ImageDraw.Draw(bg)
    line_h = 60

    # 3. Teks Punchline ATAS
    if top_text.strip():
        top_lines = textwrap.wrap(top_text.strip().upper(), width=24)
        total_top_h = len(top_lines) * line_h
        y_top = max(40, y_fg - total_top_h - 25)
        for line in top_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            draw.text(((canvas_w - lw) // 2, y_top), line, font=font, fill="white", stroke_width=7, stroke_fill="black")
            y_top += line_h

    # 4. Teks Punchline BAWAH
    if bottom_text.strip():
        bottom_lines = textwrap.wrap(bottom_text.strip().upper(), width=24)
        total_bottom_h = len(bottom_lines) * line_h
        y_bottom = min(canvas_h - total_bottom_h - 40, y_fg + fg_h + 25)
        for line in bottom_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            draw.text(((canvas_w - lw) // 2, y_bottom), line, font=font, fill="white", stroke_width=7, stroke_fill="black")
            y_bottom += line_h

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    bg.save(output_path, quality=95)
    print(f"  [PURE-MEME 4:5] Berhasil generate meme: {os.path.basename(output_path)}")
    return output_path

CURATED_MEMES = {
    "18_kenapa_perempuan_perlu_haid_teratur": {
        "memes": [
            {
                "template": "woman_cat",
                "top": "CEWEK PAS TELAT HAID 2 HARI",
                "bottom": "APAKAH UMURKU TINGGAL SEMINGGU?!"
            },
            {
                "template": "disaster_girl",
                "top": "GILIRAN HAIDNYA DATANG TEPAT WAKTU",
                "bottom": "KRAM PERUT TAPI BATIN TENANG: 'ALHAMDULILLAH MASIH NORMAL'"
            },
            {
                "template": "drake",
                "top": "ANGGAP HAID CUMA BIKIN KRAM BULANAN",
                "bottom": "SADAR HAID ITU ALARM VITAL KESEHATAN TULANG & JANTUNG"
            }
        ],
        "caption_video": (
            "Kenapa Perempuan Perlu Haid Teratur?\n\n"
            "Bukan cuma urusan kesuburan, dokter nyebut siklus haid sebagai 'Tanda Vital Kelima' tubuh perempuan! "
            "Dari perlindungan kepadatan tulang, kesehatan jantung, sampai deteksi dini stres kronis.\n\n"
            "Simak penjelasannya sampai habis dan share ke sahabatmu ya!\n\n"
            "#TemanOverthinking #SerunyaBelajar #taugaksih #KesehatanWanita #fyp"
        ),
        "caption_meme": (
            "Yang cewek pasti paham drama bulanan ini 😭 Giliran telat overthinking, giliran datang malah tepar! "
            "Tapi tau gak sih, siklus haid itu alarm paling jujur dari tubuh kita?\n\n"
            "Penjelasan sains lengkapnya udah kita spill di video sebelah (cek profil @teman_overthinking ya!) 👉\n\n"
            "#TemanOverthinking #SerunyaBelajar #taugaksih #KesehatanWanita #fyp"
        )
    },
    "19_kenapa_ayam_matanya_di_samping": {
        "memes": [
            {
                "template": "spongebob",
                "top": "MANUSIA: NOLEH LEHER PEGEL",
                "bottom": "AYAM: LIRIK DIKIT SUDUT PANDANG 300 DERAJAT AKTIF"
            },
            {
                "template": "doge_cheems",
                "top": "AYAM DENGAN RADAR 300 DERAJAT",
                "bottom": "MANUSIA NYERGAP DARI BELAKANG DIKETAWAIN AYAM"
            },
            {
                "template": "uno_25",
                "top": "NANGKEP AYAM PAKAI TANGAN KOSONG",
                "bottom": "ATAU DRAW 25 CARDS"
            }
        ],
        "caption_video": (
            "Kenapa Ayam Matanya di Samping Kepala?\n\n"
            "Bukan desain sembarangan! Di dunia fauna, posisi mata adalah garis pemisah mutlak antara siapa yang berburu dan siapa yang diburu. "
            "Ayam dibekali radar monokuler 300 derajat untuk bertahan hidup.\n\n"
            "Simak faktanya dan tulis komentar kamu ya!\n\n"
            "#TemanOverthinking #SerunyaBelajar #taugaksih #FaktaHewan #fyp"
        ),
        "caption_meme": (
            "Pantesan mau nangkep ayam dari belakang susahnya minta ampun 😂 Radar matanya ternyata hampir 300 derajat tanpa perlu noleh!\n\n"
            "Penjelasan biologis lengkapnya udah tayang di video profil sebelah ya, yuk tonton! 👉\n\n"
            "#TemanOverthinking #SerunyaBelajar #taugaksih #FaktaHewan #fyp"
        )
    },
    "20_kenapa_babi_gak_bisa_nengok_ke_atas": {
        "memes": [
            {
                "template": "pablo",
                "top": "SEMUA HEWAN PAS LIAT KEMBANG API: 'WAH INDAHNYA'",
                "bottom": "BABI: 'LANGIT TUH YANG MANA LEHER GUE GAK NYAMPE'"
            },
            {
                "template": "two_buttons",
                "top": "BABI PAS PENGEN LIAT LANGIT BIRU",
                "bottom": "SATU-SATUNYA CARA: REBAHAN TELENTANG DI TANAH"
            },
            {
                "template": "trade_offer",
                "top": "TULANG LEHER KAKU BUAT GALI TANAH",
                "bottom": "TAPI GAK BISA NENGOK KE LANGIT SEUMUR HIDUP"
            }
        ],
        "caption_video": (
            "Kenapa Babi Gak Bisa Nengok ke Atas?\n\n"
            "Secara fisik babi mustahil menatap langsung ke langit! Struktur tulang leher pendek dan otot tebal yang didesain untuk menggali tanah membatasi sudut kepalanya hanya 45 derajat.\n\n"
            "Tonton penjelasannya sampai habis ya!\n\n"
            "#TemanOverthinking #SerunyaBelajar #taugaksih #FaktaHewan #fyp"
        ),
        "caption_meme": (
            "Ternyata mitos babi gak bisa nengok ke langit itu 100% fakta anatomi biologi 😭 Mau tahu kenapa struktur lehernya bisa kaku begitu?\n\n"
            "Penjelasan lengkapnya udah kita bahas di video profil sebelah ya! Yuk tonton 👉\n\n"
            "#TemanOverthinking #SerunyaBelajar #taugaksih #FaktaHewan #fyp"
        )
    },
    "21_kenapa_gadget_selalu_punya_warna_hitam": {
        "memes": [
            {
                "template": "distracted_bf",
                "top": "LAGI GANDENG HP WARNA ESTETIK",
                "bottom": "TAPI MATA TETEP MELOTOTIN HP WARNA HITAM PEKAT"
            },
            {
                "template": "clown",
                "top": "BELI HP WARNA CERAH BIAR KECE",
                "bottom": "SAMPE RUMAH LANGSUNG DIPASANGIN CASING HITAM 15 RIBUAN"
            },
            {
                "template": "trade_offer",
                "top": "MAU KAMU MINTA WARNA APAPUN",
                "bottom": "STOK DI GUDANG YANG PALING LAKU TETEP WARNA HITAM"
            }
        ],
        "caption_video": (
            "Kenapa Gadget Selalu Punya Varian Warna Hitam?\n\n"
            "Mulai dari menyamarkan bezel layar & lubang sensor, stabilitas pigmen termurah di pabrik, sampai risiko nol stok mati bagi produsen. Warna hitam adalah raja mutlak dunia gadget!\n\n"
            "Kalian tim HP warna hitam atau warna cerah nih?\n\n"
            "#TemanOverthinking #SerunyaBelajar #taugaksih #Teknologi #fyp"
        ),
        "caption_meme": (
            "Siapa yang suka kalap liat HP warna unik tapi ujung-ujungnya tetep checkout warna hitam? 😂 Ternyata ada alasan psikologi dan rahasia pabrik di baliknya!\n\n"
            "Tonton penjelasan lengkapnya di video profil sebelah ya 👉\n\n"
            "#TemanOverthinking #SerunyaBelajar #taugaksih #Teknologi #fyp"
        )
    }
}

def generate_project_memes_and_captions(p_id: str, p_dir: str, p_title: str, p_data: dict = None):
    output_dir = os.path.join(p_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    curated = CURATED_MEMES.get(p_id)
    if not curated:
        curated = {
            "memes": [
                {
                    "template": "pablo",
                    "top": "GUE JAM 2 PAGI TIBA-TIBA KEPIKIRAN",
                    "bottom": p_title.upper()
                },
                {
                    "template": "two_buttons",
                    "top": "OTAK GUE MALAM INI",
                    "bottom": "TIDUR NYENYAK VS OVERTHINKING SEMALAMAN"
                },
                {
                    "template": "drake",
                    "top": "DIABAIKAN TERUS TIDUR",
                    "bottom": "TONTON PENJELASANNYA DI VIDEO SEBELAH"
                }
            ],
            "caption_video": (
                f"{p_title}\n\n"
                f"Ternyata di balik pertanyaan sepele ini ada penjelasan ilmiah yang bikin kita kagum! "
                f"Simak pembahasannya sampai tuntas dan share ke teman overthinking kamu ya!\n\n"
                f"#TemanOverthinking #SerunyaBelajar #taugaksih #FaktaUnik #fyp"
            ),
            "caption_meme": (
                f"Kalian pernah kepikiran hal yang sama gak nih? 😂 "
                f"Ternyata ada penjelasan ilmiahnya yang gak terduga!\n\n"
                f"Pembahasan lengkapnya udah tayang di video profil sebelah ya, yuk tonton 👉\n\n"
                f"#TemanOverthinking #SerunyaBelajar #taugaksih #FaktaUnik #fyp"
            )
        }

    # Generate 3 Pure Meme Slides
    print(f"  [MEME-ENGINE] Menghasilkan 3 pure meme (full image, top/bottom punchline) untuk: {p_id} ...")
    for idx, m in enumerate(curated["memes"]):
        m_filename = f"{p_id}_meme_{idx + 1}.jpg"
        m_out_path = os.path.join(output_dir, m_filename)
        
        create_pure_meme_image(
            template_name=m["template"],
            top_text=m.get("top", ""),
            bottom_text=m.get("bottom", ""),
            output_path=m_out_path
        )

    # Write Caption Video
    cap_video_path = os.path.join(output_dir, f"{p_id}_caption_video.txt")
    with open(cap_video_path, "w", encoding="utf-8") as f:
        f.write(curated["caption_video"].strip() + "\n")
    print(f"  [CAPTION-ENGINE] Disimpan: {os.path.basename(cap_video_path)}")

    # Write Caption Meme
    cap_meme_path = os.path.join(output_dir, f"{p_id}_caption_meme.txt")
    with open(cap_meme_path, "w", encoding="utf-8") as f:
        f.write(curated["caption_meme"].strip() + "\n")
    print(f"  [CAPTION-ENGINE] Disimpan: {os.path.basename(cap_meme_path)}")

    return True
