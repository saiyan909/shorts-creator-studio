import os
import subprocess
import json
import re

def get_audio_duration(audio_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", os.path.abspath(audio_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(json.loads(res.stdout)["format"]["duration"])

def find_vocal_boundaries(audio_path: str, total_dur: float) -> tuple:
    """
    Mendeteksi titik awal dan akhir vokal secara presisi dan aman:
    - Memberikan pre-roll aman 350ms sehingga desah nafas & kata pertama utuh 100%
    - Memberikan post-roll aman 700ms sehingga kata terakhir & peluruhan ruangan utuh 100%
    - Tidak pernah memotong jeda alami di tengah-tengah kalimat
    """
    vocal_start = 0.0
    vocal_end = total_dur

    # Cek detik awal di mana suara vokal mulai aktif (> -24dB) dan berkelanjutan (bukan ketukan mic singkat)
    check_steps_start = int(min(6.0, total_dur) * 10)
    for step in range(check_steps_start):
        t = step * 0.1
        res = subprocess.run([
            "ffmpeg", "-y", "-ss", str(t), "-t", "0.1",
            "-i", audio_path, "-af", "volumedetect", "-f", "null", "-"
        ], capture_output=True, text=True)
        m = re.search(r"max_volume:\s*(-?[0-9.]+)", res.stderr)
        if m and float(m.group(1)) > -22.0:
            # Cek apakah suara berkelanjutan dalam 0.3s ke depan untuk menghindari klik/ketukan mic
            res_next = subprocess.run([
                "ffmpeg", "-y", "-ss", str(t + 0.3), "-t", "0.2",
                "-i", audio_path, "-af", "volumedetect", "-f", "null", "-"
            ], capture_output=True, text=True)
            m_next = re.search(r"max_volume:\s*(-?[0-9.]+)", res_next.stderr)
            mv_next = float(m_next.group(1)) if m_next else -50
            if mv_next > -32.0:
                # Berikan buffer aman 350ms sebelum vokal pertama
                vocal_start = max(0.0, t - 0.35)
                break

    # Cek detik akhir dari belakang di mana suara vokal selesai (> -24dB)
    check_steps_end = int(total_dur * 10)
    limit_back = max(0, check_steps_end - 80)
    for step in range(check_steps_end, limit_back, -1):
        t = step * 0.1
        res = subprocess.run([
            "ffmpeg", "-y", "-ss", str(t), "-t", "0.1",
            "-i", audio_path, "-af", "volumedetect", "-f", "null", "-"
        ], capture_output=True, text=True)
        m = re.search(r"max_volume:\s*(-?[0-9.]+)", res.stderr)
        if m and float(m.group(1)) > -24.0:
            # Berikan buffer aman 700ms setelah vokal terakhir
            vocal_end = min(total_dur, t + 0.70)
            break

    return vocal_start, vocal_end

def enhance_and_trim_raw_voice(raw_audio_path: str, output_audio_path: str) -> str:
    """
    Memproses rekaman suara mentah Mas Adhi secara lembut & profesional:
    1. Deteksi batas awal & akhir vokal dengan buffer napas aman (tanpa memotong kata)
    2. Highpass filter 75Hz (buang rumble mic & angin AC)
    3. Noise suppression lembut (afftdn)
    4. Vocal Presence EQ (+2.0dB di 3kHz agar vokal jernih di speaker HP)
    5. Loudness Normalization standar Shorts/TikTok (-14 LUFS, True Peak -1.5dB)
    """
    raw_audio_path = os.path.abspath(raw_audio_path)
    output_audio_path = os.path.abspath(output_audio_path)
    os.makedirs(os.path.dirname(output_audio_path), exist_ok=True)

    total_dur = get_audio_duration(raw_audio_path)
    v_start, v_end = find_vocal_boundaries(raw_audio_path, total_dur)
    print(f"  [AUDIO-ENGINE] Deteksi vokal: {v_start:.2f}s sampai {v_end:.2f}s (durasi efektif: {v_end - v_start:.2f}s)")

    filter_chain = (
        "highpass=f=75,"
        "lowpass=f=12000,"
        "afftdn=nr=10:nf=-35:tn=1,"
        "equalizer=f=3000:t=q:w=1.2:g=2.0,"
        "afade=t=in:ss=0:d=0.05,"
        "loudnorm=I=-14:LRA=7:TP=-1.5"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{v_start:.3f}",
        "-to", f"{v_end:.3f}",
        "-i", raw_audio_path,
        "-af", filter_chain,
        "-c:a", "libmp3lame", "-b:a", "192k",
        output_audio_path
    ]

    print(f"  [AUDIO-ENGINE] Memproses suara mentah: {os.path.basename(raw_audio_path)} ...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg audio processing failed: {res.stderr}")

    new_duration = get_audio_duration(output_audio_path)
    print(f"  [AUDIO-ENGINE] Selesai! Suara bersih & alami tanpa terpotong: {new_duration:.2f}s")
    return output_audio_path

def slice_audio_to_scenes(processed_audio_path: str, output_dir: str, scene_durations: list) -> list:
    """
    Memotong audio master yang sudah bersih ke scene1.mp3, scene2.mp3, dst sesuai durasi adegan
    """
    os.makedirs(output_dir, exist_ok=True)
    scene_files = []
    current_start = 0.0

    for idx, dur in enumerate(scene_durations):
        out_scene_file = os.path.join(output_dir, f"scene{idx + 1}.mp3")
        cmd = [
            "ffmpeg", "-y", "-ss", str(current_start), "-t", str(dur),
            "-i", os.path.abspath(processed_audio_path),
            "-c:a", "libmp3lame", "-b:a", "192k",
            out_scene_file
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        scene_files.append(out_scene_file)
        current_start += dur

    return scene_files
