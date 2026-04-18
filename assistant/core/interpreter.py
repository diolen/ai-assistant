import re

INTENTS = {
    "search": ["где", "найди", "используется"],
    "debug": ["почему", "ошибка", "баг", "не работает"],
    "flow": ["как проходит", "поток"],
    "refactor": ["исправь", "почини"]
}

PRIORITY = ["refactor", "debug", "flow", "search"]

FIELD_ALIASES = {
    "сумма": "grand_total",
    "итог": "grand_total",
    "total": "grand_total"
}

def detect_intents(query):
    q = query.lower()
    scores = {k: 0 for k in INTENTS}

    for intent, words in INTENTS.items():
        for w in words:
            if w in q:
                scores[intent] += 1

    found = [k for k,v in scores.items() if v > 0]

    if not found:
        return ["debug"]

    found.sort(key=lambda x: PRIORITY.index(x))
    return found

def extract_field(query):
    q = query.lower()

    for k, v in FIELD_ALIASES.items():
        if k in q:
            return v

    words = re.findall(r"[a-zA-Z_]+", q)

    for w in words:
        if w.startswith("admin_"):
            continue

        if "_" in w:
            return w

    return None

def extract_filters(query):
    q = query.lower()

    filter_type = None
    grep = None
    limit = None

    if "только запись" in q or "write" in q:
        filter_type = "WRITE"
    elif "только чтение" in q or "read" in q:
        filter_type = "READ"
    elif "условия" in q or "if" in q:
        filter_type = "CONDITION"

    # grep по слову
    import re
    m = re.search(r"grep:(\w+)", q)
    if m:
        grep = m.group(1)

    # limit
    m = re.search(r"limit:(\d+)", q)
    if m:
        limit = int(m.group(1))

    return filter_type, grep, limit    

def interpret(query):
    filter_type, grep, limit = extract_filters(query)

    field = extract_field(query)
    intents = detect_intents(query)

    return {
        "field": field,
        "intents": intents,
        "filter_type": filter_type,
        "grep": grep,
        "limit": limit
    }