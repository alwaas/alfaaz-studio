"""Unit tests for Urdu Pronunciation Dictionary system."""

from app.utils.urdu_text import PronunciationDictionary, pronunciation_dict


def test_default_pronunciation_substitutions() -> None:
    """Test applying default poetic pronunciation dictionary."""
    text = "دل اور عشق کی بات"
    applied = pronunciation_dict.apply(text)

    # "دل" should be substituted with "دِل", "عشق" with "عِشق"
    assert "دِل" in applied
    assert "عِشق" in applied
    # Non-dictionary words remain unaltered
    assert "اور" in applied
    assert "کی" in applied
    assert "بات" in applied


def test_custom_pronunciation_dictionary() -> None:
    """Test adding custom entries and verifying override behavior."""
    custom_dict = PronunciationDictionary({"بہار": "بَہار"})
    assert "بَہار" in custom_dict.apply("موسم بہار آیا")

    # Add dynamically
    custom_dict.add_word("ساغر", "ساغَر")
    assert "ساغَر" in custom_dict.apply("جام و ساغر")

    # Remove entry
    removed = custom_dict.remove_word("ساغر")
    assert removed is True
    assert "ساغر" in custom_dict.apply("جام و ساغر")


def test_empty_and_whitespace_input() -> None:
    """Test pronunciation dictionary handling of empty and single-word inputs."""
    custom_dict = PronunciationDictionary()
    assert custom_dict.apply("") == ""
    assert custom_dict.apply("   ") == "   "
    assert custom_dict.apply("شعر") == "شِعر"
