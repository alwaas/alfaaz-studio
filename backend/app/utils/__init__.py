"""Utilities module initialization."""

from app.utils.urdu_text import (
    PronunciationDictionary,
    UrduTextNormalizer,
    normalize_urdu,
    pronunciation_dict,
    split_couplets,
    split_verses,
)

__all__ = [
    "UrduTextNormalizer",
    "PronunciationDictionary",
    "pronunciation_dict",
    "normalize_urdu",
    "split_verses",
    "split_couplets",
]
