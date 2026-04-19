def build_proof(flow, field, inputs=None):
    """
    V11 PROOF ENGINE

    FIXES:
    - adds semantic classification
    - improves write/read meaning
    - introduces dataflow interpretation layer
    """

    if not flow:
        return "NO FLOW DATA"

    def normalize(item):
        if isinstance(item, dict):
            return {
                "line": item.get("line"),
                "code": item.get("code") or ""
            }

        if isinstance(item, (list, tuple)):
            if len(item) >= 2:
                return {"line": item[0], "code": item[1] or ""}
            if len(item) == 1:
                return {"line": None, "code": str(item[0])}
            return {"line": None, "code": ""}

        return {"line": None, "code": str(item)}

    def safe(name):
        data = flow.get(name, [])
        return [normalize(x) for x in data if x]

    reads = safe("reads")
    writes = safe("writes")
    conditions = safe("conditions")
    calls = safe("calls")
    sequence = safe("sequence")

    def classify_write(code):
        c = code.lower()
        if "->set" in c:
            return "MUTATION"
        if "save" in c:
            return "PERSIST"
        if "=>" in c:
            return "MAPPING"
        return "ASSIGN"

    result = []

    result.append(f"FIELD: {field}")
    result.append("")

    # =========================
    # READS
    # =========================
    result.append("📖 READS (data consumption):")
    if reads:
        for r in reads:
            result.append(f"- line {r['line']}: {r['code']}")
    else:
        result.append("- none")

    result.append("")

    # =========================
    # WRITES (semantic)
    # =========================
    result.append("💾 WRITES (data mutation):")
    if writes:
        for w in writes:
            kind = classify_write(w["code"])
            result.append(f"- line {w['line']} [{kind}]: {w['code']}")
    else:
        result.append("- none")

    result.append("")

    # =========================
    # CONDITIONS
    # =========================
    result.append("⚙ CONDITIONS (branching logic):")
    if conditions:
        for c in conditions:
            result.append(f"- line {c['line']}: {c['code']}")
    else:
        result.append("- none")

    result.append("")

    # =========================
    # CALLS
    # =========================
    result.append("📞 CALLS (side effects):")
    if calls:
        for c in calls:
            result.append(f"- line {c['line']}: {c['code']}")
    else:
        result.append("- none")

    result.append("")

    # =========================
    # INPUT DETECTION
    # =========================
    result.append("📥 INPUT:")
    if inputs:
        for i in inputs:
            result.append(f"- line {i['line']}: {i['code']}")
    else:
        result.append("- none")

    result.append("")

    # =========================
    # SEMANTIC SUMMARY (NEW)
    # =========================
    result.append("=== SUMMARY ===")

    has_input = bool(inputs)
    has_write = bool(writes)
    has_read = bool(reads)

    if has_input and has_write:
        result.append("STATUS: INPUT_BOUND_FIELD (request → mutation)")
    elif has_write and not has_input:
        result.append("STATUS: DERIVED_OR_INTERNAL_FIELD")
    elif has_read and not has_write:
        result.append("STATUS: READONLY_FIELD")
    elif has_write:
        result.append("STATUS: MUTATED_FIELD")
    else:
        result.append("STATUS: UNUSED_FIELD")

    return "\n".join(result)