import re

# -------------------------
# INTENT RULES (deterministic)
# -------------------------

INTENTS = {
    "search": ["где", "найди", "используется", "использование"],
    "debug": ["почему", "ошибка", "баг", "не работает", "сломалось"],
    "flow": ["как проходит", "поток", "цепочка", "откуда берётся"],
    "refactor": ["исправь", "почини", "улучши", "перепиши"]
}

PRIORITY = ["refactor", "debug", "flow", "search"]


# -------------------------
# FIELD EXTRACTION
# -------------------------

FIELD_ALIASES = {
    "сумма": "grand_total",
    "итог": "grand_total",
    "total": "grand_total"
}


def detect_intents(query: str):
    q = query.lower()

    scores = {k: 0 for k in INTENTS}

    for intent, words in INTENTS.items():
        for w in words:
            if w in q:
                scores[intent] += 1

    found = [k for k, v in scores.items() if v > 0]

    # если ничего не найдено → безопасный fallback (но НЕ debug по умолчанию)
    if not found:
        return ["search"]

    found.sort(key=lambda x: PRIORITY.index(x))
    return found


def extract_field(query: str):
    """
    Детерминированное извлечение поля без fallback-магии.
    """

    q = query.lower()

    # 1. явные алиасы
    for k, v in FIELD_ALIASES.items():
        if k in q:
            return v

    # 2. прямое совпадение snake_case
    candidates = re.findall(r"[a-zA-Z_]+", q)

    for c in candidates:
        if "_" in c:
            # исключаем controller/method слова
            if c.startswith("admin_"):
                continue
            return c

    # 3. ничего не найдено → None (ВАЖНО)
    return None


def extract_filters(query: str):
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

    # grep: grep:word
    m = re.search(r"grep:(\w+)", q)
    if m:
        grep = m.group(1)

    # limit: limit:10
    m = re.search(r"limit:(\d+)", q)
    if m:
        limit = int(m.group(1))

    return filter_type, grep, limit


# -------------------------
# MAIN INTERPRETER
# -------------------------

def interpret(query: str):
    """
    V10:
    - без fallback поля
    - без hardcoded grand_total
    - полностью детерминированный output
    """

    intents = detect_intents(query)
    field = extract_field(query)
    filter_type, grep, limit = extract_filters(query)

    return {
        "intents": intents,
        "field": field,
        "filter_type": filter_type,
        "grep": grep,
        "limit": limit
    }