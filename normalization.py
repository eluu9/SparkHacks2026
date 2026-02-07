import re

def normalizeString(input: str) -> str:
    stringList = input.split()
    for i in range(len(stringList)):
        if (stringList[i] == None):
            stringList[i] = ""
        stringList[i] = stringList[i].lower()  # Convert to lowercase
        stringList[i] = re.sub(r"[^a-z0-9-&]", "", stringList[i])  # Remove non-alphanumeric characters
    return " ".join(stringList)


def normalizeUPCAndEPN(input: str) -> str:
    stringList = normalizeString(input)
    upcString = "".join(stringList)
    upcString = re.sub(r"[^0-9]", "", upcString)  # Extract only digits
    if upcString == "" or len(upcString) > 13:
        return ""  # Return empty string if no digits found
    if len(upcString) < 12:
        upcString = upcString.zfill(12)
    return upcString

def normalizeMPN(input: str) -> str:
    return normalizeString(input)

def normalizeModel(input: str) -> str:
    return normalizeString(input)

def normalizeBrand(input: str) -> str:
    return normalizeString(input)

