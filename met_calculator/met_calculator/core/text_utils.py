"""Text helper utilities for normalization and matching."""

from __future__ import annotations

import unicodedata


def normalize_text(value: str) -> str:
    """Normalize to lowercase ASCII text with compact spaces."""
    no_accents = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    lowered = no_accents.lower()
    compact = " ".join(lowered.split())
    return compact
