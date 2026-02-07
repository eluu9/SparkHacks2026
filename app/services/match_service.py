"""Score and rank search results against kit items."""

import difflib

from normalization import normalize_string


def score_title(kit_item, search_item):
    """Compare kit item name to search result title using fuzzy matching."""
    kit_name = kit_item.get("name")
    kit_specs = kit_item.get("specs_to_search", [])
    search_name = search_item.get("title")

    if not kit_name or not search_name:
        return 0, []

    normalized_kit_name = normalize_string(kit_name)
    normalized_search_name = normalize_string(search_name)
    specs_found = 0

    similarity = difflib.SequenceMatcher(
        None, normalized_kit_name, normalized_search_name
    ).ratio()

    if similarity < 0.30:
        return 0, []

    for spec in kit_specs:
        if normalize_string(spec) in normalized_search_name:
            specs_found += 1

    # Direct substring match is a strong signal
    if normalized_kit_name in normalized_search_name:
        return 0.85, ["Direct Keyword Match"]
    if similarity > 0.85 and specs_found > 0:
        return 0.90, ["High Title Similarity with Specs Found"]
    if similarity > 0.80 and specs_found >= 1:
        return 0.75, ["Medium Title Similarity with Specs Found"]
    if similarity > 0.75:
        return 0.60, ["Fair Title Similarity"]
    if similarity > 0.70:
        return 0.40, ["Low Title Similarity"]
    return 0, []


def calculate_confidence(kit_item, search_item):
    """Wrapper that returns a confidence score and reasoning list."""
    return score_title(kit_item, search_item)


def rank_candidates(kit_item, search_items):
    """Return search results sorted by descending confidence."""
    ranked = []

    for search_item in search_items:
        confidence, reason = calculate_confidence(kit_item, search_item)
        if confidence > 0:
            ranked.append({
                "search_item": search_item,
                "confidence": confidence,
                "reason": reason,
                "source": search_item.get("source", "unknown"),
                "url": search_item.get("url", ""),
            })

    ranked.sort(key=lambda x: x["confidence"], reverse=True)
    return ranked