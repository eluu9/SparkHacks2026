from normalization import *
import difflib

def scoreTitle(kitItem, searchItem):
    kitName = kitItem['name']
    kitSpecs = kitItem['specs_to_search']
    searchName = searchItem['title']

    if not kitName or not searchName:
        return (0, [])
    
    normalizedKitName = normalizeString(kitName)
    normalizedSearchName = normalizeString(searchName)
    specsFound = 0

    similarity = difflib.SequenceMatcher(None, normalizedKitName, normalizedSearchName).ratio()
    if similarity < 0.60:
        return(0, [])

    for spec in kitSpecs:
        normalizedSpecs = normalizeString(spec)
        if (normalizedSpecs in normalizedSearchName):
            specsFound += 1
    if similarity > 0.85 and specsFound > 0:
        return (0.90, ["High Title Similarity with Specs Found"])
    elif similarity > 0.80 and specsFound >= 1:
        return (0.75, ["Medium Title Similarity with Specs Found"])
    elif similarity > 0.75:
        return (0.60, ["Fair Title Similarity"])
    elif similarity > 0.70:
        return (0.40, ["Low Title Similarity"])
    return (0, [])

def calculateConfidence(kitItem, searchItem):
    confidence = 0
    reason = []

    confidence, reason = scoreTitle(kitItem, searchItem)
    return confidence, reason

def rankCandidates(kitItem, searchItems):
    ranked = []

    for searchItem in searchItems:
        confidence, reason = calculateConfidence(kitItem, searchItem)
        if confidence > 0:
            ranked.append({"Search Item": searchItem, "Confidence": confidence, "Reason": reason, "Source": searchItem.get("source", "unknown"), "URL": searchItem.get("url", "")})
    ranked.sort(key=lambda x: x["Confidence"], reverse=True)
    return ranked
