def find_field_flow(code, field):
    """
    V10.7 CLEAN ANALYZER

    FIXES:
    - точные WRITE
    - строгие CONDITIONS
    - CALLS только с участием field
    - правильный приоритет операторов
    """

    if not code or not field:
        return _empty_flow()

    lines = code.split("\n")

    reads = []
    writes = []
    saves = []
    conditions = []
    calls = []
    sequence = []

    field_l = field.lower()

    for i, line in enumerate(lines, 1):

        lower = line.lower()

        if field_l not in lower:
            continue  # ускорение

        clean = line.strip()

        # =========================
        # SAVE (выше WRITE)
        # =========================
        if "->save(" in lower or "save(" in lower:
            saves.append({
                "line": i,
                "code": clean
            })
            continue

        # =========================
        # WRITE (FIX PRIORITY)
        # =========================
        if (
            f"{field_l} =" in lower
            or f"'{field_l}' =>" in lower
            or f'"{field_l}" =>' in lower
            or (f"[{field_l}]" in lower and "=" in lower)
            or ("->set(" in lower and field_l in lower)
        ):
            writes.append({
                "line": i,
                "code": clean
            })
            continue

        # =========================
        # CONDITIONS (STRICT)
        # =========================
        if lower.strip().startswith("if"):
            conditions.append({
                "line": i,
                "code": clean
            })
            continue

        # =========================
        # CALLS (только если поле участвует)
        # =========================
        if "->" in lower and "(" in lower and field_l in lower:
            calls.append({
                "line": i,
                "code": clean
            })
            continue

        # =========================
        # READ (DEFAULT)
        # =========================
        reads.append({
            "line": i,
            "code": clean
        })

    return {
        "reads": reads,
        "writes": writes,
        "saves": saves,
        "conditions": conditions,
        "calls": calls,
        "sequence": sequence
    }


def find_request_input(code, field):
    """
    V10.7 CLEAN INPUT DETECTOR

    FIXES:
    - убран шум
    - добавлен $_GET
    - строгая фильтрация
    """

    if not code or not field:
        return []

    lines = code.split("\n")

    results = []
    field_l = field.lower()

    for i, line in enumerate(lines, 1):

        lower = line.lower()

        if field_l not in lower:
            continue

        if (
            "request->data" in lower
            or "$_post" in lower
            or "$_get" in lower
        ):
            results.append({
                "line": i,
                "code": line.strip()
            })

    return results


def _empty_flow():
    return {
        "reads": [],
        "writes": [],
        "saves": [],
        "conditions": [],
        "calls": [],
        "sequence": []
    }