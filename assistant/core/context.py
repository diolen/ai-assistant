def extract_field(query):
    words = query.lower().split()

    priority_fields = [
        "grand_total",
        "total",
        "sum",
        "amount"
    ]

    # 1. сначала ищем реальные поля
    for w in words:
        if w in priority_fields or "_" in w:
            return w

    # 2. fallback на underscore-like tokens
    for w in words:
        if "_" in w:
            return w

    return None