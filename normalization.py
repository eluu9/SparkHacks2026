"""Text normalization utilities for fuzzy product matching."""

import re


def normalize_string(value):
    """Lowercase and strip non-alphanumeric characters for comparison."""
    if not value:
        return ""

    tokens = value.split()
    for i, token in enumerate(tokens):
        token = token.lower()
        tokens[i] = re.sub(r"[^a-z0-9-&]", "", token)

    return " ".join(tokens)

