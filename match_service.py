from normalization import *
import difflib

def scoreTier1(kitItem, searchItem):
    kitUPC = kitItem['identifier_hints']['upc']
    searchUPC = searchItem['upc']

    normalizedKitUPC = normalizeUPCAndEPN(kitUPC)
    normalizedSearchUPC = normalizeUPCAndEPN(searchUPC)
    if normalizedKitUPC and normalizedSearchUPC and normalizedKitUPC == normalizedSearchUPC:
        return (0.95, f"Exact UPC Match: {normalizedKitUPC}")
    return (0, [])

def scoreTier2(kitItem, searchItem):
    kitMPN = kitItem['identifier_hints']['mpn']
    searchMPN = searchItem['mpn']
    normalizedKitMPN = normalizeMPN(kitMPN)
    normalizedSearchMPN = normalizeMPN(searchMPN)

    kitBrand = kitItem['identifier_hints']['brand']
    searchBrand = searchItem['brand']
    normalizedKitBrand = normalizeBrand(kitBrand)
    normalizedSearchBrand = normalizeBrand(searchBrand)

    if normalizedKitMPN == normalizedSearchMPN:
        if normalizedKitBrand == normalizedSearchBrand:
            return (0.88, ["Exact MPN and Brand Match"])
        return (0.75, ["Exact MPN Match"])
    return (0, [])

def scoreTier3(kitItem, searchItem):
    kitModel = kitItem['identifier_hints']['model']
    searchModel = searchItem['model']
    normalizedKitModel = normalizeModel(kitModel)
    normalizedSearchModel = normalizeModel(searchModel)

    kitBrand = kitItem['identifier_hints']['brand']
    searchBrand = searchItem['brand']
    normalizedKitBrand = normalizeBrand(kitBrand)
    normalizedSearchBrand = normalizeBrand(searchBrand)

    if normalizedKitModel == normalizedSearchModel:
        if normalizedKitBrand == normalizedSearchBrand:
            return (0.82, ["Exact Model and Brand Match"])
        return (0.70, ["Exact Model Match"])
    return (0, [])

def scoreTier4(kitItem, searchItem):
    kitName = kitItem['name']
    searchName = searchItem['title']
    normalizedKitName = normalizeBrand(kitName)
    normalizedSearchName = normalizeBrand(searchName)
    return (difflib.SequenceMatcher(None, normalizedKitName, normalizedSearchName).ratio(), ["No Exact Name Match"])



