import os
import subprocess
import json
import re

def get_audio_duration(audio_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "json", audio_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(json.loads(res.stdout)["format"]["duration"])

def detect_audio_scene_splits(audio_path: str, expected_scenes: int = 5) -> list:
    """Mendeteksi titik potong adegan berdasarkan jeda hening / jeda napas pembicara secara presisi"""
    total_dur = get_audio_duration(audio_path)
    cmd = [
        "ffmpeg", "-i", audio_path,
        "-af", "silencedetect=noise=-25dB:d=0.35",
        "-f", "null", "-"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    lines = res.stderr.split("\n")
    
    silence_points = []
    for line in lines:
        if "silence_end:" in line:
            parts = line.split("silence_end:")
            if len(parts) > 1:
                val = parts[1].split("|")[0].strip()
                try:
                    silence_points.append(float(val))
                except ValueError:
                    pass

    # Titik target ideal jika dibagi rata
    ideal_targets = [(total_dur / expected_scenes) * i for i in range(1, expected_scenes)]
    splits = []
    # Untuk setiap target ideal, cari jeda hening terdekat dalam jendela +/- 4.5s
    # agar pergantian adegan jatuh tepat di hening/napas pembicara, bukan memotong kata
    for target in ideal_targets:
        min_prev = (splits[-1] + 3.0) if splits else 3.0
        candidates = [sp for sp in silence_points if abs(sp - target) <= 4.5 and sp >= min_prev]
        if candidates:
            best = min(candidates, key=lambda sp: abs(sp - target))
            splits.append(round(best, 2))
        else:
            splits.append(round(target, 2))

    # Konversi ke durasi masing-masing adegan
    durations = []
    prev = 0.0
    for s in splits:
        durations.append(round(s - prev, 2))
        prev = s
    durations.append(round(total_dur - prev, 2))
    return durations

def render_project(project_data: dict, project_dir: str, custom_audio_path: str = None) -> str:
    build_dir = os.path.join(project_dir, "build")
    output_dir = os.path.join(project_dir, "output")
    os.makedirs(build_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    output_video = os.path.join(output_dir, "final_shorts.mp4")
    scenes = project_data.get("scenes", [])
    if not scenes:
        raise ValueError("No scenes found in project data")

    clip_files = []
    scene_durations = []
    audio_files = []

    # Auto-detect existing custom/cleaned voice if not explicitly passed
    if not custom_audio_path:
        clean_voice = os.path.join(project_dir, "audio", "voice_master_clean.mp3")
        custom_voice = os.path.join(project_dir, "audio", "custom_voice.mp3")
        if os.path.exists(clean_voice):
            custom_audio_path = clean_voice
        elif os.path.exists(custom_voice):
            custom_audio_path = custom_voice

    # If custom audio is provided for the entire video
    if custom_audio_path and os.path.exists(custom_audio_path):
        from engine.audio_processor import enhance_and_trim_raw_voice
        clean_voice_path = os.path.join(project_dir, "audio", "voice_master_clean.mp3")
        if os.path.abspath(custom_audio_path) == os.path.abspath(clean_voice_path):
            master_audio = custom_audio_path
        else:
            try:
                master_audio = enhance_and_trim_raw_voice(custom_audio_path, clean_voice_path)
                print(f"  [AUTO-AUDIO] Berhasil membersihkan noise & memotong hening 2s awal/akhir!")
            except Exception as e:
                print(f"  [AUTO-AUDIO Warning] Fallback ke audio asli karena: {e}")
                master_audio = custom_audio_path

        total_custom_dur = get_audio_duration(master_audio)
        print(f"  [RENDER] Menggunakan voiceover bersih: {master_audio} ({total_custom_dur:.2f}s)")
        # Otomatis mendeteksi pembagian durasi adegan dari jeda hening / napas
        scene_durations = detect_audio_scene_splits(master_audio, len(scenes))
        print(f"  [AUTO-SYNC] Durasi adegan terdeteksi otomatis: {scene_durations}")
    else:
        # Standard mode: per-scene audio
        for s in scenes:
            a_path = os.path.join(project_dir, s.get("audio", f"audio/scene{s['id']}.mp3"))
            if not os.path.exists(a_path):
                raise FileNotFoundError(f"Audio file not found: {a_path}")
            dur = get_audio_duration(a_path)
            scene_durations.append(dur)
            audio_files.append(a_path)

        # Concat audio clips
        audio_concat_txt = os.path.join(build_dir, "audios.txt")
        with open(audio_concat_txt, "w") as f:
            for af in audio_files:
                f.write(f"file '{os.path.abspath(af)}'\n")

        master_audio = os.path.join(build_dir, "master_audio.mp3")
        print("  [RENDER] Merging scene audio tracks...")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", audio_concat_txt,
            "-c:a", "libmp3lame", "-b:a", "192k", master_audio
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 1. Insert Thumbnail Opening Hook Frame (0.9s at t=0)
    thumb_path = os.path.join(project_dir, "output", "thumbnail.jpg")
    if not os.path.exists(thumb_path):
        thumb_path = os.path.join(project_dir, "thumbnail.jpg")
    
    intro_dur = 0.9
    has_thumb_intro = False
    
    if os.path.exists(thumb_path) and len(scene_durations) > 0 and scene_durations[0] > (intro_dur + 1.5):
        has_thumb_intro = True
        print(f"  [RENDER] Menyisipkan Thumbnail 'KENAPA' di detik 0:00 ({intro_dur}s) untuk cover instan...")
        thumb_clip = os.path.join(build_dir, "clip_0_thumb.mp4")
        thumb_cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", thumb_path,
            "-t", f"{intro_dur:.3f}",
            "-vf", "scale=1080:1920,fps=30",
            "-c:v", "libx264", "-preset", "veryfast", "-threads", "12", "-crf", "18",
            "-pix_fmt", "yuv420p",
            thumb_clip
        ]
        subprocess.run(thumb_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        clip_files.append(thumb_clip)

    # Render each scene clip with Ken Burns motion (supports 2-3 images per scene!)
    for idx, s in enumerate(scenes):
        sc_id = s.get("id", idx + 1)
        dur = scene_durations[idx]
        if idx == 0 and has_thumb_intro:
            dur = round(dur - intro_dur, 3)

        # Detect multiple images for this scene
        assets_dir = os.path.join(project_dir, "assets")
        scene_img_candidates = []
        
        # Check explicit images field
        if s.get("images") and isinstance(s["images"], list):
            for im_rel in s["images"]:
                im_abs = os.path.join(project_dir, im_rel)
                if os.path.exists(im_abs) and os.path.getsize(im_abs) > 5000:
                    scene_img_candidates.append(im_abs)
                    
        # Check numbered images: scene{id}_1.jpg, scene{id}_2.jpg, scene{id}_3.jpg
        if not scene_img_candidates and os.path.exists(assets_dir):
            for i_num in range(1, 5):
                cand = os.path.join(assets_dir, f"scene{sc_id}_{i_num}.jpg")
                if os.path.exists(cand) and os.path.getsize(cand) > 5000:
                    scene_img_candidates.append(cand)

        # Fallback to single image
        if not scene_img_candidates:
            single_img = os.path.join(project_dir, s.get("image", f"assets/scene{sc_id}.jpg"))
            if os.path.exists(single_img):
                scene_img_candidates.append(single_img)

        # Emergency fallback if no image at all
        if not scene_img_candidates:
            avail = [os.path.join(assets_dir, f) for f in os.listdir(assets_dir) if f.endswith(('.jpg', '.png'))] if os.path.exists(assets_dir) else []
            if avail:
                scene_img_candidates.append(avail[0])
            elif os.path.exists(thumb_path):
                scene_img_candidates.append(thumb_path)
            else:
                from PIL import Image
                im_def = Image.new("RGB", (1080, 1920), color=(15, 23, 42))
                def_path = os.path.join(assets_dir, f"scene{sc_id}.jpg")
                im_def.save(def_path, quality=90)
                scene_img_candidates.append(def_path)

        num_imgs = len(scene_img_candidates)
        sub_dur = dur / num_imgs
        print(f"  [RENDER] Scene {sc_id} ({dur:.2f}s total | {num_imgs} visual dinamis | {sub_dur:.2f}s per gambar)...")

        for sub_i, img_p in enumerate(scene_img_candidates):
            sub_clip_path = os.path.join(build_dir, f"clip_{sc_id}_{sub_i+1}.mp4")
            clip_files.append(sub_clip_path)

            sub_frames = int(round(sub_dur * 30))
            if sub_frames < 10:
                sub_frames = 10

            # Alternating Ken Burns motion:
            # Genap: Zoom In | Ganjil: Zoom Out
            if (idx + sub_i) % 2 == 0:
                vf = f"zoompan=z='min(zoom+0.0006,1.15)':d={sub_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"
            else:
                vf = f"zoompan=z='if(lte(zoom,1.0),1.14,max(1.001,zoom-0.0005))':d={sub_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"

            render_cmd = [
                "ffmpeg", "-y", "-loop", "1", "-i", img_p,
                "-t", f"{sub_dur:.3f}",
                "-vf", vf,
                "-c:v", "libx264", "-preset", "veryfast", "-threads", "12", "-crf", "18",
                "-pix_fmt", "yuv420p",
                sub_clip_path
            ]
            subprocess.run(render_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Concat video clips
    concat_txt = os.path.join(build_dir, "clips.txt")
    with open(concat_txt, "w") as f:
        for c in clip_files:
            f.write(f"file '{os.path.abspath(c)}'\n")

    concat_video = os.path.join(build_dir, "raw_video.mp4")
    print("  [RENDER] Stitching video clips...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-c", "copy", concat_video
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Generate ASS Subtitles
    ass_file = os.path.join(build_dir, "subtitles.ass")
    sub_style = project_data.get("subtitle_style", {})
    font_name = sub_style.get("font_name", "Arial Black")
    font_size = sub_style.get("font_size", 52)
    prim_col = sub_style.get("primary_color", "&H00FFFFFF")
    hi_col = sub_style.get("highlight_color", "&H0000E5FF")
    margin_v = sub_style.get("margin_v", 430)

    ass_lines = [
        "[Script Info]",
        f"Title: {project_data.get('title', 'Shorts')}",
        "ScriptType: v4.00+",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.601",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,{font_name},{font_size},{prim_col},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,5,2,2,60,60,{margin_v},1",
        f"Style: Highlight,{font_name},{font_size + 2},{hi_col},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,6,3,2,60,60,{margin_v},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    def fmt_ts(sec: float) -> str:
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        cs = int(round((sec - int(sec)) * 100))
        if cs >= 100:
            cs = 99
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    cum_time = 0.0
    for idx, s in enumerate(scenes):
        sub_list = s.get("subtitles", [])
        scene_dur = scene_durations[idx]

        if not sub_list:
            cum_time += scene_dur
            continue

        # Subtitle mulai tepat saat suara mulai (detik 0.15 pada adegan pertama, 0.05 pada adegan berikutnya)
        cur_offset = 0.15 if idx == 0 else 0.05
        available_dur = max(0.8, scene_dur - cur_offset)

        # Hitung bobot kata untuk tiap baris subtitle agar durasi tampilan proporsional dengan panjang teks
        weights = [max(1, len(re.findall(r'\w+', sub.get("text", "")))) for sub in sub_list]
        total_w = sum(weights) or 1

        # Berikan jeda napas kecil di akhir adegan (~0.25s) sebelum pindah adegan
        active_speech_dur = max(0.6, available_dur - 0.25)

        for sub_i, sub in enumerate(sub_list):
            seg_dur = (weights[sub_i] / total_w) * active_speech_dur
            start = cum_time + cur_offset
            end = start + seg_dur
            cur_offset += seg_dur

            style_name = "Highlight" if sub.get("highlight", False) else "Default"
            text = sub["text"].replace("\n", "\\n")
            ass_lines.append(
                f"Dialogue: 0,{fmt_ts(start)},{fmt_ts(end)},{style_name},,0,0,{margin_v},,{text}"
            )

        cum_time += scene_dur

    with open(ass_file, "w") as f:
        f.write("\n".join(ass_lines) + "\n")

    # Burn subtitles and combine master audio
    print("  [RENDER] Burning subtitles and exporting final MP4...")
    final_cmd = [
        "ffmpeg", "-y",
        "-i", concat_video,
        "-i", master_audio,
        "-vf", f"ass={ass_file}",
        "-c:v", "libx264", "-preset", "veryfast", "-threads", "12", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_video
    ]
    subprocess.run(final_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  [SUCCESS] Video ready at: {output_video}")

    # Salin juga ke format nama file yang sesuai judul/ID project
    p_id = project_data.get("id", os.path.basename(project_dir))
    named_video = os.path.join(output_dir, f"{p_id}.mp4")
    try:
        import shutil
        shutil.copyfile(output_video, named_video)
        print(f"  [SUCCESS] Video dengan nama judul project: {named_video}")
    except Exception as e_copy:
        print(f"  [NAMED-VIDEO Warning] {e_copy}")

    return named_video

