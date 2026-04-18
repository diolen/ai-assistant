import re

def extract_field(query):
    words = re.findall(r"[a-zA-Z_]+", query)

    for w in words:
        if "_" in w:
            return w

    return None