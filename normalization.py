import re

def normalizeString(input: str):
    if input == None or input == "":
        return ""
    stringList = input.split()
    for i in range(len(stringList)):
        stringList[i] = stringList[i].lower()  # Convert to lowercase
        stringList[i] = re.sub(r"[^a-z0-9-&]", "", stringList[i])  # Remove non-alphanumeric characters
    return " ".join(stringList)

