import re


# =========================
# FIELD EXTRACTOR (V11.3)
# =========================
def extract_field(query):
    """
    V11.3 FIXED:

    - убран мусорный fallback
    - admin_* НЕ считается field
    - строгое ранжирование
    - безопасная логика без container leakage
    """

    if not query:
        return None

    words = query.lower().split()

    priority_fields = [
        "grand_total",
        "total",
        "sum",
        "amount",
        "type_id",
        "user_id",
        "status",
        "price",
        "cost"
    ]

    blacklist = {
        "search", "controller", "index", "view",
        "add", "edit", "delete"
    }

    # =========================
    # 1. STRICT MATCH
    # =========================
    for w in words:
        if w in priority_fields:
            return w

    # =========================
    # 2. SAFE FIELD MATCH (underscore only)
    # =========================
    for w in words:

        if w.startswith("admin_"):
            continue

        if w in blacklist:
            continue

        if "_" in w and len(w) > 3:
            return w

    # =========================
    # 3. NO FALLBACK (IMPORTANT FIX)
    # =========================
    return None


# =========================
# 🔥 NESTED FIELD EXTRACTOR (V11.3 FIXED)
# =========================
def extract_nested_fields(code):
    """
    Extracts real structured fields from:

    - $this->request->data['Search']['field']
    - Search['field']
    - Search.field
    """

    if not code:
        return []

    fields = set()

    patterns = [
        # CakePHP style deep array
        r"\$this->request->data\[['\"]Search['\"]\]\[['\"]([^'\"]+)['\"]\]",

        # generic PHP array
        r"Search\[['\"]([^'\"]+)['\"]\]",

        # object-style access
        r"Search\.([a-zA-Z0-9_]+)"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, code, re.IGNORECASE)

        for m in matches:
            if not m:
                continue

            m = m.lower()

            # safety filter
            if len(m) <= 2:
                continue

            if m in {"search", "controller", "request"}:
                continue

            fields.add(m)

    return list(fields)