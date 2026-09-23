"""Unit tests for Urdu text normalization and poetic structure parsing."""

from app.utils.urdu_text import (
    URDU_COMMA,
    URDU_KHATMA,
    URDU_QUESTION,
    UrduTextNormalizer,
    normalize_urdu,
    split_couplets,
    split_verses,
)


def test_unicode_normalization_and_char_mapping() -> None:
    """Test NFC normalization and mapping Arabic variants to standard Urdu characters."""
    # Arabic Kaf ك (U+0643) should map to Urdu Kaf ک (U+06A9)
    raw_kaf = "كتاب"
    normalized_kaf = UrduTextNormalizer.normalize_unicode(raw_kaf)
    assert normalized_kaf == "کتاب"

    # Arabic Yeh ي (U+064A) should map to Urdu Choti Yeh ی (U+06CC)
    raw_yeh = "زندگي"
    normalized_yeh = UrduTextNormalizer.normalize_unicode(raw_yeh)
    assert normalized_yeh == "زندگی"

    # Kashida / Tatweel removal
    raw_tatweel = "شـــعــــر"
    cleaned = UrduTextNormalizer.normalize_unicode(raw_tatweel)
    assert cleaned == "شعر"


def test_urdu_punctuation_preservation_and_conversion() -> None:
    """Test Western punctuation conversion to authentic Urdu punctuation marks."""
    # Western dot -> Urdu Khatma (۔)
    text_with_dot = "یہ ایک خوبصورت شعر ہے."
    converted = UrduTextNormalizer.normalize_punctuation(text_with_dot)
    assert URDU_KHATMA in converted
    assert "." not in converted

    # Western question mark -> Urdu question mark (؟)
    text_with_q = "کیا یہ سچ ہے?"
    converted_q = UrduTextNormalizer.normalize_punctuation(text_with_q)
    assert URDU_QUESTION in converted_q
    assert "?" not in converted_q

    # Western comma -> Urdu comma (،)
    text_with_comma = "پھول, خوشبو اور بہار"
    converted_comma = UrduTextNormalizer.normalize_punctuation(text_with_comma)
    assert URDU_COMMA in converted_comma
    assert "," not in converted_comma


def test_clean_text_complete_pipeline() -> None:
    """Test end-to-end cleaning pipeline including whitespace and newlines."""
    dirty_text = "  كيا  حال   ہے?   زندگي كيسي ہے.  "
    cleaned = normalize_urdu(dirty_text)

    # Should contain proper Urdu characters and punctuation without messy whitespace
    assert "کیا" in cleaned
    assert "زندگی" in cleaned
    assert URDU_QUESTION in cleaned
    assert URDU_KHATMA in cleaned


def test_split_verses() -> None:
    """Test splitting poetry into individual verses (Misras)."""
    ghazal = """
    ہستی اپنی حباب کی سی ہے
    یہ نمائش سراب کی سی ہے

    نازکی اس کے لب کی کیا کہئے
    پنکھڑی اک گلاب کی سی ہے
    """
    verses = split_verses(ghazal)
    assert len(verses) == 4
    assert verses[0] == "ہستی اپنی حباب کی سی ہے"
    assert verses[1] == "یہ نمائش سراب کی سی ہے"
    assert verses[2] == "نازکی اس کے لب کی کیا کہئے"
    assert verses[3] == "پنکھڑی اک گلاب کی سی ہے"


def test_split_couplets() -> None:
    """Test grouping verses into couplets (Ash'ar)."""
    ghazal = """
    دل سے جو بات نکلتی ہے اثر رکھتی ہے
    پر نہیں طاقت پرواز مگر رکھتی ہے
    قدسی الاصل ہے رفعت پہ نظر رکھتی ہے
    خاک سے اٹھتی ہے گردوں پہ گزر رکھتی ہے
    """
    couplets = split_couplets(ghazal)
    assert len(couplets) == 2
    assert couplets[0][0] == "دل سے جو بات نکلتی ہے اثر رکھتی ہے"
    assert couplets[0][1] == "پر نہیں طاقت پرواز مگر رکھتی ہے"

    # Test odd number of lines
    odd_poem = "مصرع اول\nمصرع دوم\nمصرع سوم"
    odd_couplets = split_couplets(odd_poem)
    assert len(odd_couplets) == 2
    assert odd_couplets[1][0] == "مصرع سوم"
    assert odd_couplets[1][1] == ""
