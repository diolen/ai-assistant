def build_proof(flow, field, inputs=None):
    """
    V10.3.2 FINAL SAFE PROOF LAYER
    - fully hardened against tuple/dict/null corruption
    - stable schema for engine + lifecycle
    """

    if not flow:
        return "NO FLOW DATA"

    # =========================
    # NORMALIZER (HARDENED)
    # =========================
    def normalize(item):

        if isinstance(item, dict):
            return {
                "line": item.get("line"),
                "code": item.get("code") or ""
            }

        if isinstance(item, (list, tuple)):

            if len(item) >= 2:
                return {
                    "line": item[0],
                    "code": item[1] or ""
                }

            if len(item) == 1:
                return {
                    "line": None,
                    "code": str(item[0])
                }

            return {"line": None, "code": ""}

        return {
            "line": None,
            "code": str(item)
        }

    # =========================
    # SAFE EXTRACTOR
    # =========================
    def safe_list(name):
        data = flow.get(name, [])
        if not data:
            return []

        cleaned = []
        for x in data:
            n = normalize(x)

            # ❗ HARD FILTER (IMPORTANT FIX)
            if not n["code"]:
                continue

            cleaned.append(n)

        return cleaned

    reads = safe_list("reads")
    writes = safe_list("writes")
    conditions = safe_list("conditions")
    calls = safe_list("calls")
    sequence = safe_list("sequence")

    result = []

    result.append(f"FIELD: {field}")
    result.append("")

    # -----------------------
    # READS
    # -----------------------
    result.append("📖 READS:")
    result.extend(
        f"- line {r['line']}: {r['code']}" for r in reads
    ) if reads else result.append("- none")

    result.append("")

    # -----------------------
    # WRITES
    # -----------------------
    result.append("💾 WRITES:")
    result.extend(
        f"- line {w['line']}: {w['code']}" for w in writes
    ) if writes else result.append("- none")

    result.append("")

    # -----------------------
    # CONDITIONS
    # -----------------------
    result.append("⚙ CONDITIONS:")
    result.extend(
        f"- line {c['line']}: {c['code']}" for c in conditions
    ) if conditions else result.append("- none")

    result.append("")

    # -----------------------
    # CALLS
    # -----------------------
    result.append("📞 CALLS:")
    result.extend(
        f"- line {c['line']}: {c['code']}" for c in calls
    ) if calls else result.append("- none")

    result.append("")

    # -----------------------
    # SEQUENCE
    # -----------------------
    result.append("🔁 SEQUENCE:")
    result.extend(
        f"- line {s['line']}: {s['code']}" for s in sequence
    ) if sequence else result.append("- none")

    # -----------------------
    # SUMMARY
    # -----------------------
    result.append("")
    result.append("=== SUMMARY ===")

    if writes:
        result.append("STATUS: FIELD IS WRITTEN")
    elif reads:
        result.append("STATUS: FIELD IS ONLY READ")
    else:
        result.append("STATUS: FIELD NOT USED")

    return "\n".join(result)