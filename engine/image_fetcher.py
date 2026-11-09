#!/usr/bin/env python3
"""
Adhi Studio - Web Image Fetcher HD
Mencari dan mengunduh foto/visual beresolusi tinggi (9:16 vertical 1080x1920)
bebas watermark dari Web (Bing Images & Wikimedia Commons) untuk tiap adegan.
Mendukung 2-3 gambar per scene (total 10-15 gambar per video Shorts/Reels).
"""

import os
import re
import ssl
import time
import urllib.request
import urllib.parse
from PIL import Image

CTX = ssl._create_unverified_context()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def search_bing_images(query: str, max_results: int = 8) -> list:
    """Mencari URL gambar resolusi tinggi dari Bing async search"""
    url = f"https://www.bing.com/images/async?q={urllib.parse.quote(query)}&mmasync=1"
    req = urllib.request.Request(url, headers=HEADERS)
    urls = []
    try:
        with urllib.request.urlopen(req, timeout=12, context=CTX) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            matches = re.findall(r'murl&quot;:&quot;(https?://[^&]+)&quot;', html)
            for m in matches:
                # Filter out low-res or troublesome formats
                if not any(ext in m.lower() for ext in [".svg", ".gif", ".ico"]):
                    urls.append(m)
                if len(urls) >= max_results:
                    break
    except Exception as e:
        print(f"    [BING SEARCH WARNING] {e}")
    return urls

def search_wikimedia_images(query: str, max_results: int = 5) -> list:
    """Mencari gambar bebas hak cipta dari Wikimedia Commons API"""
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&gsrlimit={max_results}&prop=imageinfo&iiprop=url|size&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "AdhiStudio/1.0 (contact@temanoverthinking.com)"})
    urls = []
    try:
        with urllib.request.urlopen(req, timeout=10, context=CTX) as resp:
            import json
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for pid, p in pages.items():
                info = p.get("imageinfo", [{}])[0]
                u = info.get("url")
                if u and not u.lower().endswith((".svg", ".gif", ".ogg", ".webm")):
                    urls.append(u)
    except Exception as e:
        print(f"    [WIKIMEDIA WARNING] {e}")
    return urls

def download_and_crop_to_vertical(image_url: str, output_path: str, target_w: int = 1080, target_h: int = 1920) -> bool:
    """Mengunduh gambar dan memotong/menyesuaikan (center crop) ke ukuran vertikal 9:16 (1080x1920)"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    req = urllib.request.Request(image_url, headers=HEADERS)
    temp_path = output_path + ".tmp"
    try:
        with urllib.request.urlopen(req, timeout=15, context=CTX) as resp:
            data = resp.read()
            if len(data) < 5000:
                return False
            with open(temp_path, "wb") as f:
                f.write(data)

        # Proses cropping pintar ke 9:16
        with Image.open(temp_path) as im:
            im = im.convert("RGB")
            w, h = im.size

            target_ratio = target_w / target_h
            current_ratio = w / h

            if current_ratio > target_ratio:
                # Gambar lebih lebar -> potong sisi kiri dan kanan
                new_w = int(h * target_ratio)
                left = (w - new_w) // 2
                im_cropped = im.crop((left, 0, left + new_w, h))
            else:
                # Gambar lebih tinggi -> potong atas dan bawah (fokus sedikit di atas tengah)
                new_h = int(w / target_ratio)
                top = max(0, int((h - new_h) * 0.35))
                im_cropped = im.crop((0, top, w, top + new_h))

            # Resize dengan anti-aliasing tajam
            im_final = im_cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
            im_final.save(output_path, "JPEG", quality=92)

        if os.path.exists(temp_path):
            os.remove(temp_path)
        return True
    except Exception as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        return False

def generate_scene_search_queries(project_title: str, scene_num: int, scene_text: str, scene_prompt: str) -> list:
    """Menghasilkan kata kunci pencarian yang relevan dan variatif untuk adegan tersebut"""
    # Bersihkan teks
    clean_text = re.sub(r'[^\w\s]', ' ', scene_text).strip()
    words = clean_text.split()
    
    # Ambil frasa penting dari teks adegan
    topic_clean = project_title.replace("Kenapa", "").replace("kenapa", "").strip()
    
    queries = []
    # Query 1: Spesifik teks adegan
    if len(words) >= 4:
        queries.append(f"{topic_clean} {' '.join(words[:5])}")
    
    # Query 2: Dari prompt visual yang sudah ada (diambil kata kunci pentingnya)
    prompt_clean = re.sub(r'9:16 vertical.*|warm lighting.*|Pixar style.*', '', scene_prompt, flags=re.I).strip()
    if prompt_clean:
        queries.append(prompt_clean)
        
    # Query 3: Topik umum + variasi
    variations = [
        f"{topic_clean} closeup photography",
        f"{topic_clean} facts science",
        f"{topic_clean} funny illustration",
        f"{topic_clean} human expression",
        f"{topic_clean} nature science HD"
    ]
    queries.append(variations[scene_num % len(variations)])
    return queries

def ensure_multi_images_for_project(project_data: dict, project_dir: str, images_per_scene: int = 2) -> dict:
    """
    Memastikan setiap adegan dalam project memiliki 2-3 gambar berkualitas tinggi di assets/.
    Mengisi assets/scene{id}_1.jpg, assets/scene{id}_2.jpg, dst.
    """
    assets_dir = os.path.join(project_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    title = project_data.get("title", "")
    scenes = project_data.get("scenes", [])

    print(f"  [IMAGE ENGINE] Menyiapkan {images_per_scene} gambar HD per scene (total ~{len(scenes)*images_per_scene} gambar)...")

    for s_idx, sc in enumerate(scenes, 1):
        sc_id = sc.get("id", s_idx)
        sc_text = sc.get("text", "")
        sc_prompt = sc.get("prompt", "")
        
        # Simpan daftar path gambar untuk scene ini
        scene_images = []
        queries = generate_scene_search_queries(title, sc_id, sc_text, sc_prompt)

        for img_idx in range(1, images_per_scene + 1):
            target_file = os.path.join(assets_dir, f"scene{sc_id}_{img_idx}.jpg")
            
            # Jika file sudah ada dan ukurannya > 15KB (bukan placeholder kosong), gunakan yang sudah ada
            if os.path.exists(target_file) and os.path.getsize(target_file) > 15000:
                scene_images.append(f"assets/scene{sc_id}_{img_idx}.jpg")
                continue

            print(f"    [FETCH] Scene {sc_id} Gambar {img_idx}/{images_per_scene}...")
            # Coba cari kandidat URL dari Bing dan Wikimedia
            candidates = []
            for q in queries:
                b_urls = search_bing_images(q, max_results=6)
                candidates.extend(b_urls)
                if len(candidates) >= 8:
                    break
            
            if len(candidates) < 3:
                w_urls = search_wikimedia_images(f"{title} science", max_results=4)
                candidates.extend(w_urls)

            download_success = False
            # Coba unduh dari kandidat URL
            for cand_url in candidates:
                if download_and_crop_to_vertical(cand_url, target_file):
                    download_success = True
                    break

            # Fallback jika gagal: gunakan visual fallback styled card atau duplikasi yang ada
            if not download_success or not os.path.exists(target_file):
                # Cek jika ada scene{sc_id}.jpg sebelumnya yang valid
                legacy_single = os.path.join(assets_dir, f"scene{sc_id}.jpg")
                if os.path.exists(legacy_single) and os.path.getsize(legacy_single) > 15000:
                    import shutil
                    shutil.copyfile(legacy_single, target_file)
                    download_success = True

            if download_success:
                scene_images.append(f"assets/scene{sc_id}_{img_idx}.jpg")
            else:
                # Emergency fallback high-res card
                c_bg = (15, 23, 42) if img_idx % 2 == 1 else (24, 30, 48)
                fallback_im = Image.new("RGB", (1080, 1920), c_bg)
                fallback_im.save(target_file, quality=90)
                scene_images.append(f"assets/scene{sc_id}_{img_idx}.jpg")

        sc["images"] = scene_images
        # Backward compatibility
        if scene_images:
            sc["image"] = scene_images[0]

    return project_data
