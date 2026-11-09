import asyncio
import os

try:
    import edge_tts
except ImportError:
    edge_tts = None

async def generate_scene_audio(text: str, output_path: str, voice: str = "id-ID-ArdiNeural", rate: str = "+5%"):
    if edge_tts is None:
        raise RuntimeError("Modul edge-tts belum terinstal. Install dengan: pip install edge-tts")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)
    return output_path

def generate_all_audio(project_data: dict, project_dir: str):
    if edge_tts is None:
        print("  ⚠️ [TTS Warning] Modul edge_tts belum terinstal. Audio TTS dilewati.")
        return
    voice = project_data.get("voice", "id-ID-ArdiNeural")
    rate = project_data.get("voice_rate", "+5%")
    audio_dir = os.path.join(project_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    async def _run():
        for scene in project_data.get("scenes", []):
            out_file = os.path.join(audio_dir, f"scene{scene['id']}.mp3")
            await generate_scene_audio(scene["text"], out_file, voice, rate)
            print(f"  [TTS] Generated audio for Scene {scene['id']}")

    asyncio.run(_run())
