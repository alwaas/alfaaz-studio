"""Urdu Text Processing, Normalization, Poetry Verse Chunking, and Pronunciation."""

import re
import unicodedata

# Standard Urdu punctuation marks
URDU_KHATMA = "\u06D4"      # ۔ (Urdu Full Stop / Khatma)
URDU_QUESTION = "\u061F"    # ؟ (Urdu Question Mark)
URDU_COMMA = "\u060C"       # ، (Urdu Comma)
EXCLAMATION = "!"           # !

URDU_PUNCTUATION = {URDU_KHATMA, URDU_QUESTION, URDU_COMMA, EXCLAMATION}

# Character replacement maps for standardizing Urdu Unicode
URDU_CHAR_MAP: dict[str, str] = {
    "\u0643": "\u06A9",  # Arabic Kaf ك -> Urdu Kaf ک
    "\u0649": "\u06CC",  # Arabic Alef Maksura ى -> Urdu Choti Yeh ی
    "\u064A": "\u06CC",  # Arabic Yeh ي -> Urdu Choti Yeh ی
    "\u06C2": "\u06C1\u0654",  # Heh Goal with Hamza
    "\u06C3": "\u06C1\u0654",  # Teh Marbuta Goal
    "\u0629": "\u06C1",  # Arabic Teh Marbuta ة -> Urdu Heh ہ
    "\u0640": "",        # Kashida / Tatweel (elongation) -> remove
}

# Standard dictionary mapping words to phonetically explicit Aerab-annotated equivalents
DEFAULT_PRONUNCIATION_DICT: dict[str, str] = {
    "دل": "دِل",        # Dil
    "گل": "گُل",        # Gul
    "عشق": "عِشق",      # Ishq
    "شعر": "شِعر",      # She'r
    "محبت": "مَحَبَّت",   # Mohabbat
    "غالب": "غالِب",    # Ghalib
    "اقبال": "اِقبال",   # Iqbal
    "شاعری": "شاعِری",   # Sha'iri
    "خواب": "خواHome", # Khwab (silent wao)
    "خواہش": "خواہِش",  # Khwahish
    "وفا": "وَفا",       # Wafa
    "ستم": "سِتَم",      # Sitam
    "نگاہ": "نِگاہ",     # Nigah
    "چمن": "چَمَن",     # Chaman
}


class PronunciationDictionary:
    """Manager for Urdu phonetic and aerab pronunciation mappings."""

    def __init__(self, custom_dict: dict[str, str] | None = None) -> None:
        self.dictionary: dict[str, str] = dict(DEFAULT_PRONUNCIATION_DICT)
        if custom_dict:
            self.dictionary.update(custom_dict)

    def add_word(self, word: str, phonetic_spelling: str) -> None:
        """Add or override a word pronunciation mapping."""
        self.dictionary[word.strip()] = phonetic_spelling.strip()

    def remove_word(self, word: str) -> bool:
        """Remove a word from the pronunciation dictionary."""
        return self.dictionary.pop(word.strip(), None) is not None

    def apply(self, text: str) -> str:
        """Apply pronunciation substitutions on whole words."""
        if not text.strip():
            return text

        words = text.split()
        substituted = [self.dictionary.get(w, w) for w in words]
        return " ".join(substituted)


# Singleton pronunciation instance
pronunciation_dict = PronunciationDictionary()


class UrduTextNormalizer:
    """Comprehensive Urdu text cleaner, normalizer, and poetic structure parser."""

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """
        Normalize text into Unicode Canonical Composition (NFC) form
        and map Arabic character variants to standard Urdu glyphs.
        """
        if not text:
            return ""

        # Normalize to NFC
        normalized = unicodedata.normalize("NFC", text)

        # Standardize character variants
        for arabic_char, urdu_char in URDU_CHAR_MAP.items():
            normalized = normalized.replace(arabic_char, urdu_char)

        return normalized

    @staticmethod
    def normalize_punctuation(text: str) -> str:
        """
        Convert Western punctuation to authentic Urdu punctuation marks
        while preserving spacing and rhythmic pauses.
        """
        if not text:
            return ""

        # Western full stop -> Urdu Khatma (only when not part of decimal/URL)
        text = re.sub(r"(?<!\d)\.(?!\d)", f" {URDU_KHATMA} ", text)
        # Western question mark -> Urdu question mark
        text = text.replace("?", f" {URDU_QUESTION} ")
        # Western comma -> Urdu comma
        text = text.replace(",", f" {URDU_COMMA} ")

        # Clean redundant spaces around punctuation
        text = re.sub(r"\s+", " ", text)
        for p in URDU_PUNCTUATION:
            text = text.replace(f" {p}", p)

        return text.strip()

    @staticmethod
    def clean_text(text: str, preserve_newlines: bool = True) -> str:
        """
        Full text cleaning pipeline: Unicode normalization, punctuation mapping,
        and whitespace cleanup.
        """
        if not text:
            return ""

        # Normalize unicode
        cleaned = UrduTextNormalizer.normalize_unicode(text)

        if preserve_newlines:
            lines = cleaned.splitlines()
            cleaned_lines = [
                UrduTextNormalizer.normalize_punctuation(line.strip())
                for line in lines
            ]
            # Collapse more than two consecutive empty lines
            result = "\n".join(cleaned_lines)
            return re.sub(r"\n{3,}", "\n\n", result).strip()
        else:
            cleaned = UrduTextNormalizer.normalize_punctuation(cleaned)
            return re.sub(r"\s+", " ", cleaned).strip()

    @staticmethod
    def split_verses(text: str) -> list[str]:
        """
        Split poetry into individual verses (Misras), discarding empty lines.
        """
        cleaned = UrduTextNormalizer.clean_text(text, preserve_newlines=True)
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        return lines

    @staticmethod
    def split_couplets(text: str) -> list[tuple[str, str]]:
        """
        Group verses into couplets (Ash'ar), where each couplet has two lines (Misra-e-Ula, Misra-e-Sani).
        If the verse count is odd, the last couplet pairs with an empty second line.
        """
        verses = UrduTextNormalizer.split_verses(text)
        couplets: list[tuple[str, str]] = []

        for i in range(0, len(verses), 2):
            misra_1 = verses[i]
            misra_2 = verses[i + 1] if i + 1 < len(verses) else ""
            couplets.append((misra_1, misra_2))

        return couplets


# Convenience function exports
normalize_urdu = UrduTextNormalizer.clean_text
split_verses = UrduTextNormalizer.split_verses
split_couplets = UrduTextNormalizer.split_couplets

