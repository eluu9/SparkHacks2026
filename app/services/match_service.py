from normalization import *
import difflib

def scoreTier1(kitItem, searchItem):
    kitUPC = kitItem['identifier_hints']['upc']
    searchUPC = searchItem['upc']

    normalizedKitUPC = normalizeUPCAndEPN(kitUPC)
    normalizedSearchUPC = normalizeUPCAndEPN(searchUPC)
    if normalizedKitUPC and normalizedSearchUPC and normalizedKitUPC == normalizedSearchUPC:
        return (0.95, [f"Exact UPC Match"])
    return (0, [])

def scoreTier2(kitItem, searchItem):
    kitMPN = kitItem['identifier_hints']['mpn']
    searchMPN = searchItem['mpn']
    normalizedKitMPN = normalizeMPN(kitMPN)
    normalizedSearchMPN = normalizeMPN(searchMPN)

    #kitBrand = kitItem['identifier_hints']['brand']
    #searchBrand = searchItem['brand']
    #normalizedKitBrand = normalizeBrand(kitBrand)
    #normalizedSearchBrand = normalizeBrand(searchBrand)

    if normalizedKitMPN == normalizedSearchMPN:
        #if normalizedKitBrand == normalizedSearchBrand:
        #    return (0.88, ["Exact MPN and Brand Match"])
        return (0.75, ["Exact MPN Match"])
    return (0, [])

def scoreTier3(kitItem, searchItem):
    kitModel = kitItem['identifier_hints']['model']
    searchModel = searchItem['model']
    normalizedKitModel = normalizeModel(kitModel)
    normalizedSearchModel = normalizeModel(searchModel)

    #kitBrand = kitItem['identifier_hints']['brand']
    #searchBrand = searchItem['brand']
    #normalizedKitBrand = normalizeBrand(kitBrand)
    #normalizedSearchBrand = normalizeBrand(searchBrand)

    if normalizedKitModel == normalizedSearchModel:
        #if normalizedKitBrand == normalizedSearchBrand:
        #    return (0.82, ["Exact Model and Brand Match"])
        return (0.70, ["Exact Model Match"])
    return (0, [])

def scoreTier4(kitItem, searchItem):
    kitName = kitItem['name']
    kitSpecs = kitItem['specs_to_search']
    searchName = searchItem['title']
    normalizedKitName = normalizeString(kitName)
    normalizedSearchName = normalizeString(searchName)

    similarity = difflib.SequenceMatcher(None, normalizedKitName, normalizedSearchName).ratio()
    if similarity < 0.60:
        return(0, [])

    specsFound = 0
    for spec in kitSpecs:
        normalizedSpecs = normalizeString(spec)
        if (normalizedSpecs in normalizedSearchName):
            specsFound += 1
    if similarity > 0.85 and specsFound > 0:
        return (0.70, ["High Title Similarity with Specs Found"])
    elif similarity > 0.80 and specsFound >= 1:
        return (0.65, ["Medium Title Similarity with Specs Found"])
    elif similarity > 0.75:
        return (0.50, ["Low Title Similarity with No Specs Found"])
    return (0, [])

def calculateConfidence(kitItem, searchItem):
    confidence = 0
    reason = []

    confidence, reason = scoreTier1(kitItem, searchItem)
    if confidence > 0:
        return confidence, reason
    confidence, reason = scoreTier2(kitItem, searchItem)
    if confidence > 0:
        return confidence, reason
    confidence, reason = scoreTier3(kitItem, searchItem)
    if confidence > 0:
        return confidence, reason
    confidence, reason = scoreTier4(kitItem, searchItem)
    return confidence, reason

def rankCandidates(kitItem, searchItems):
    ranked = []

    for searchItem in searchItems:
        confidence, reason = calculateConfidence(kitItem, searchItem)
        ranked.append({"Search Item": searchItem, "Confidence": confidence, "Reason": reason})
    ranked.sort(key=lambda x: x["Confidence"], reverse=True)
    return ranked
