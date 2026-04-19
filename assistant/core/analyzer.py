import re


def find_field_flow(code, field):
    """
    V11.3 CLEAN DATAFLOW ENGINE (STABLE)

    FIXES:
    - case-safe detection
    - no condition pollution in READ
    - strict WRITE matching
    - CALLS only when field is argument or property access
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

    # =========================
    # SAFE WRITE PATTERNS (case-safe)
    # =========================
    write_patterns = [
        rf"\$\w*{re.escape(field)}\s*=",        # $var = field
        rf"['\"]{re.escape(field)}['\"]\s*=>",  # 'field' =>
        rf"\[{re.escape(field)}\]\s*=",         # [field] =
        r"->set\("
    ]

    for i, line in enumerate(lines, 1):

        lower = line.lower()
        clean = line.strip()

        if field_l not in lower:
            continue

        # =========================
        # SAVE
        # =========================
        if "->save(" in lower:
            saves.append({"line": i, "code": clean})
            continue

        # =========================
        # WRITE (STRICT)
        # =========================
        if any(re.search(p, line) for p in write_patterns):
            writes.append({"line": i, "code": clean})
            continue

        # =========================
        # CONDITIONS (FIXED SEPARATION)
        # =========================
        if lower.strip().startswith("if"):
            conditions.append({"line": i, "code": clean})
            continue

        # =========================
        # CALLS (STRICT FIELD RELATION ONLY)
        # =========================
        if "->" in lower and "(" in lower:
            if (
                f"{field_l}" in lower or
                f"${field_l}" in lower or
                f"['{field_l}']" in lower or
                f'["{field_l}"]' in lower
            ):
                calls.append({"line": i, "code": clean})
                continue

        # =========================
        # READ (SAFE VALUE CONTEXT ONLY)
        # =========================
        if (
            field_l in lower
            and "=" not in lower
            and not lower.strip().startswith("if")
            and "return" not in lower
        ):
            reads.append({"line": i, "code": clean})

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
    V11.3 INPUT DETECTOR (STRICT + SAFE)
    """

    if not code or not field:
        return []

    lines = code.split("\n")

    results = []
    field_l = field.lower()

    pattern = re.compile(
        r"(request->data|\$_post|\$_get)\[['\"]" + re.escape(field) + r"['\"]\]",
        re.IGNORECASE
    )

    for i, line in enumerate(lines, 1):
        if pattern.search(line):
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