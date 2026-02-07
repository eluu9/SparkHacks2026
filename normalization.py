import re

def normalizeString(input: str):
    if input == None or input == "":
        return ""
    stringList = input.split()
    for i in range(len(stringList)):
        stringList[i] = stringList[i].lower()  # Convert to lowercase
        stringList[i] = re.sub(r"[^a-z0-9-&]", "", stringList[i])  # Remove non-alphanumeric characters
    return " ".join(stringList)


def normalizeUPCAndEPN(input: str):
    if input == None or input == "":
        return ""
    stringList = normalizeString(input)
    upcString = "".join(stringList)
    upcString = re.sub(r"[^0-9]", "", upcString)  # Extract only digits
    if len(upcString) > 13:
        return ""  # Return empty string if no digits found
    if len(upcString) < 12:
        upcString = upcString.zfill(12)
    return upcString

def normalizeMPN(input: str) -> str:
    if input == None or input == "":
        return ""
    return normalizeString(input)

def normalizeModel(input: str) -> str:
    if input == None or input == "":
        return ""
    return normalizeString(input)

def normalizeBrand(input: str) -> str:
    if input == None or input == "":
        return ""   
    return normalizeString(input)

