"""Unit tests for Urdu Nastaliq ASS and SRT Subtitle Generator."""

import tempfile
from pathlib import Path

from app.services.subtitles import (
    ASSSubtitleBuilder,
    SubtitleVerse,
    format_ass_time,
    format_srt_time,
    generate_srt_content,
)
from app.services.tts.provider import WordTimestamp


def test_time_formatting() -> None:
    """Verifies precision time formatting for ASS and SRT subtitles."""
    assert format_ass_time(0.0) == "0:00:00.00"
    assert format_ass_time(3.456) == "0:00:03.46"
    assert format_ass_time(75.8) == "0:01:15.80"
    assert format_ass_time(3661.05) == "1:01:01.05"

    assert format_srt_time(0.0) == "00:00:00,000"
    assert format_srt_time(3.456) == "00:00:03,456"
    assert format_srt_time(75.8) == "00:01:15,800"


def test_ass_header_and_styles() -> None:
    """Verifies that ASS script info sets 9:16 resolution and Nastaliq styles."""
    builder = ASSSubtitleBuilder(
        font_name="Noto Nastaliq Urdu",
        font_size=62,
        resolution_x=1080,
        resolution_y=1920,
    )
    header = builder.build_header("Test Reel")

    assert "PlayResX: 1080" in header
    assert "PlayResY: 1920" in header
    assert "Style: Nastaliq_Main,Noto Nastaliq Urdu,62" in header
    assert "Style: Nastaliq_Title" in header
    assert "Style: Nastaliq_Poet" in header


def test_ass_content_generation() -> None:
    """Verifies dialog generation with and without karaoke word highlights."""
    builder = ASSSubtitleBuilder()

    verses = [
        SubtitleVerse(
            text="دل ناداں تجھے ہوا کیا ہے",
            start_time=0.5,
            end_time=3.5,
            words=[
                WordTimestamp(word="دل", start_time=0.5, end_time=1.0),
                WordTimestamp(word="ناداں", start_time=1.0, end_time=1.8),
                WordTimestamp(word="تجھے", start_time=1.8, end_time=2.3),
                WordTimestamp(word="ہوا", start_time=2.3, end_time=2.8),
                WordTimestamp(word="کیا", start_time=2.8, end_time=3.1),
                WordTimestamp(word="ہے", start_time=3.1, end_time=3.5),
            ],
        ),
        SubtitleVerse(
            text="آخر اس درد کی دوا کیا ہے",
            start_time=3.8,
            end_time=6.8,
        ),
    ]

    # 1. With karaoke
    content_k = builder.build_ass_content(
        verses=verses,
        title="غزل غالب",
        poet_name="مرزا اسد اللہ خان غالب",
        enable_karaoke=True,
    )
    assert "Dialogue: 0,0:00:00.00," in content_k
    assert "غزل غالب" in content_k
    assert "مرزا اسد اللہ خان غالب" in content_k
    assert r"{\k50}دل" in content_k
    assert r"{\k80}ناداں" in content_k
    assert "آخر اس درد کی دوا کیا ہے" in content_k

    # 2. Without karaoke
    content_plain = builder.build_ass_content(
        verses=verses,
        enable_karaoke=False,
    )
    assert r"\k" not in content_plain
    assert "دل ناداں تجھے ہوا کیا ہے" in content_plain


def test_ass_file_writing() -> None:
    """Verifies writing ASS file to filesystem."""
    builder = ASSSubtitleBuilder()
    verses = [
        SubtitleVerse(
            text="ہزاروں خواہشیں ایسی کہ ہر خواہش پہ دم نکلے",
            start_time=0.0,
            end_time=4.0,
        )
    ]

    with tempfile.NamedTemporaryFile(suffix=".ass", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        written = builder.write_ass_file(tmp_path, verses, title="غالب")
        assert written.exists()
        text = written.read_text(encoding="utf-8")
        assert "ہزاروں خواہشیں ایسی" in text
    finally:
        tmp_path.unlink(missing_ok=True)


def test_srt_generation() -> None:
    """Verifies generation of standard SRT subtitles."""
    verses = [
        SubtitleVerse(
            text="پہلا مصرع",
            start_time=1.0,
            end_time=3.5,
        ),
        SubtitleVerse(
            text="دوسرا مصرع",
            start_time=3.8,
            end_time=6.0,
        ),
    ]

    srt = generate_srt_content(verses)
    assert "1\n00:00:01,000 --> 00:00:03,500\nپہلا مصرع" in srt
    assert "2\n00:00:03,800 --> 00:00:06,000\nدوسرا مصرع" in srt
