from normalization import *

def scoreTier1(kitItem, searchItem):
    kitUPC = kitItem['identifier']['upc']
    searchUPC = searchItem['upc']

    if kitUPC and searchUPC:
        normalizedKitUPC = normalizeUPCAndEPN(kitUPC)
        normalizedSearchUPC = normalizeUPCAndEPN(searchUPC)
        if normalizedKitUPC and normalizedSearchUPC and normalizedKitUPC == normalizedSearchUPC:
            return (95, f"Exact UPC match: {normalizedKitUPC}")
    


def scoreTier2(kitItem, searchItem):
    normalizeMPN(kitItem)
    return (80, "MPN Match")


def scoreTier3(kitItem, searchItem):
    normalizeModel(kitItem)
    return (60, "Model Match")


def scoreTier4(kitItem, searchItem):
    normalizeBrand(kitItem)
    return (40, "Brand Match")

