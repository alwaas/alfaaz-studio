#!/usr/bin/env python3
"""Headless Sample Reel Generator for AlfaazStudio.

Generates a complete, publication-ready 9:16 Instagram Reel MP4 video
from classic Urdu poetry without launching the web UI.

Pipeline:
1. Urdu Text Normalization & Verse Splitting
2. Neural / Synthetic Speech Audio Synthesis
3. Cinematic Audio DSP Mastering (Warm EQ + Mushaira Reverb + Compressor + BGM)
4. Kinetic ASS Subtitle Generation with Nastaliq Typography
5. FFmpeg 9:16 Video Rendering (1080x1920 MP4)
"""

import asyncio
import io
import os
import sys
import time
from pathlib import Path

# Configure UTF-8 for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.dsp import audio_dsp
from app.services.renderer import REEL_THEMES, reel_renderer
from app.services.subtitles import ASSSubtitleBuilder, SubtitleVerse
from app.services.tts.mock_provider import MockTTSProvider
from app.utils.urdu_text import UrduTextNormalizer


async def generate_sample_reel(
    poetry_text: str = "دل ناداں تجھے ہوا کیا ہے\nآخر اس درد کی دوا کیا ہے",
    title: str = "دل ناداں",
    poet: str = "مرزا غالب",
    theme_id: str = "velvet-gold",
    output_filename: str = "sample_ghalib_reel.mp4",
) -> Path:
    """Headless automated reel generator."""
    print("=" * 60)
    print("   الفاظ اسٹوڈیو • ALFAAZSTUDIO SAMPLE REEL GENERATOR")
    print("=" * 60)
    print(f"Title: {title}")
    print(f"Poet:  {poet}")
    print(f"Theme: {theme_id}")
    print("-" * 60)

    start_time = time.time()

    # 1. Text Normalization
    print("› Step 1: Normalizing Urdu poetry text & splitting verses...")
    clean_poetry = UrduTextNormalizer.clean_text(poetry_text)
    verses_raw = UrduTextNormalizer.split_verses(clean_poetry)
    for idx, v in enumerate(verses_raw, start=1):
        print(f"   [{idx}] {v}")

    # 2. Audio Synthesis
    print("\n› Step 2: Synthesizing speech voiceover...")
    import soundfile as sf
    tts = MockTTSProvider()
    tts_result = await tts.synthesize(text=clean_poetry, speed=1.0)
    audio_data, sr = sf.read(io.BytesIO(tts_result.audio_bytes), dtype="float32")
    print(f"   ✓ Synthesized {len(audio_data)} audio samples at {sr} Hz")
    print(f"   ✓ Generated {len(tts_result.word_timestamps)} word-level timestamp markers")

    # 3. DSP Mastering
    print("\n› Step 3: Applying acoustic mastering chain...")
    from app.services.dsp import AudioDSPParams

    dsp_params = AudioDSPParams(
        eq_warmth_db=3.0,
        eq_air_db=2.0,
        reverb_wet=0.15,
        reverb_room_size=0.5,
        enable_compression=True,
        compressor_threshold_db=-16.0,
    )
    mastered_audio = audio_dsp.mix_and_master(
        voice_audio=audio_data,
        bgm_audio=None,
        sample_rate=sr,
        bgm_volume=0.22,
        ducking_depth_db=-14.0,
        dsp_params=dsp_params,
    )
    duration = round(len(mastered_audio) / float(sr), 3)
    print(f"   ✓ Mastered duration: {duration:.2f}s (Warm EQ, Schroeder Reverb, Compressor, BGM)")

    # Save audio temporarily
    temp_dir = Path("temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_audio_path = temp_dir / "sample_voiceover.wav"
    wav_bytes = audio_dsp.audio_to_wav_bytes(mastered_audio, sr)
    temp_audio_path.write_bytes(wav_bytes)

    # 4. Generate Subtitles
    print("\n› Step 4: Generating ASS Nastaliq subtitles with karaoke highlight...")
    from app.services.tts.provider import WordTimestamp

    parsed_words = [
        WordTimestamp(
            word=w["word"],
            start_time=w["start_time"],
            end_time=w["end_time"],
        )
        for w in tts_result.word_timestamps
    ]

    verse_dur = duration / float(max(1, len(verses_raw)))
    subtitle_verses = [
        SubtitleVerse(
            text=verse_text,
            start_time=round(i * verse_dur, 2),
            end_time=round((i + 1) * verse_dur, 2),
            words=parsed_words,
        )
        for i, verse_text in enumerate(verses_raw)
    ]

    # 5. FFmpeg Video Rendering
    print("\n› Step 5: Executing FFmpeg 9:16 vertical render engine (1080x1920)...")
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(parents=True, exist_ok=True)
    output_path = outputs_dir / output_filename

    rendered_reel = await reel_renderer.render_reel(
        audio_path=temp_audio_path,
        verses=subtitle_verses,
        output_path=output_path,
        duration=duration,
        title=title,
        poet_name=poet,
        theme_id=theme_id,
        fps=30,
        font_name="Noto Nastaliq Urdu",
        font_size=60,
        enable_karaoke=True,
    )

    elapsed = time.time() - start_time
    file_size_kb = output_path.stat().st_size / 1024.0

    print("-" * 60)
    print("✅ REEL GENERATION COMPLETE!")
    print(f"Output File:     {output_path.resolve()}")
    print(f"File Size:       {file_size_kb:.1f} KB")
    print(f"Aspect Ratio:    9:16 Vertical (1080x1920)")
    print(f"Frame Rate:      30 fps (H.264 / AAC)")
    print(f"Duration:        {duration:.2f} seconds")
    print(f"Processing Time: {elapsed:.2f} seconds")
    print("=" * 60)

    # Cleanup temp audio
    temp_audio_path.unlink(missing_ok=True)
    return output_path


if __name__ == "__main__":
    asyncio.run(generate_sample_reel())
