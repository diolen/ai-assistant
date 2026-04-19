def extract_field(query):
    """
    V10.6 FIX:
    - не теряет field если это admin_*
    - умный fallback
    - приоритет реальных полей
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

    # =========================
    # 1. STRICT FIELD MATCH
    # =========================
    for w in words:
        if w in priority_fields:
            return w

    # =========================
    # 2. NORMAL FIELDS (underscore, НЕ admin)
    # =========================
    for w in words:

        if "controller" in w:
            continue

        if len(w) < 3:
            continue

        if "_" in w and not w.startswith("admin_"):
            return w

    # =========================
    # 3. FALLBACK: admin_* (ВАЖНО)
    # =========================
    for w in words:
        if w.startswith("admin_"):
            return w

    # =========================
    # 4. LAST WORD FALLBACK
    # =========================
    if words:
        return words[-1]

    return None