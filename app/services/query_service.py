def generate_item_queries(kit_json):
    queries = []
    
    for section in kit_json.get("sections", []):
        for item in section.get("items", []):
            query = build_query_for_item(item)
            queries.append(query)
    
    return {"items": queries}


def build_query_for_item(item):
    item_key = item.get("item_key", "")
    name = item.get("name", "")
    specs = item.get("specs_to_search", [])
    query_terms = item.get("query_terms", [])
    hints = item.get("identifier_hints", {})
    
    top_specs = " ".join(specs[:3]) if specs else ""
    clean_query = f"{name} {top_specs}".strip()
    
    synonyms = " ".join(query_terms[:5]) if query_terms else ""
    expanded_query = f"{clean_query} {synonyms}".strip()
    
    fingerprint = {
        "brand": hints.get("brand"),
        "mpn": hints.get("mpn"),
        "model": hints.get("model"),
        "upc": hints.get("upc"),
        "must_have_tokens": specs[:5] if specs else []
    }
    
    return {
        "item_key": item_key,
        "clean_query": clean_query,
        "expanded_query": expanded_query,
        "strict_match_fingerprint": fingerprint
    }


