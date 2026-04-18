def build_proof(flow, field, inputs=None):
    """
    V10: Proof layer = formatter, not analyzer
    """

    if not flow:
        return "NO FLOW DATA"

    result = []

    result.append(f"FIELD: {field}")
    result.append("")

    # -----------------------
    # READS
    # -----------------------
    result.append("📖 READS:")
    if flow.get("reads"):
        for r in flow["reads"]:
            result.append(f"- line {r['line']}: {r['code']}")
    else:
        result.append("- none")

    result.append("")

    # -----------------------
    # WRITES
    # -----------------------
    result.append("💾 WRITES:")
    if flow.get("writes"):
        for w in flow["writes"]:
            result.append(f"- line {w['line']}: {w['code']}")
    else:
        result.append("- none")

    result.append("")

    # -----------------------
    # CONDITIONS
    # -----------------------
    result.append("⚙ CONDITIONS:")
    if flow.get("conditions"):
        for c in flow["conditions"]:
            result.append(f"- line {c['line']}: {c['code']}")
    else:
        result.append("- none")

    result.append("")

    # -----------------------
    # CALLS
    # -----------------------
    result.append("📞 CALLS:")
    if flow.get("calls"):
        for c in flow["calls"]:
            result.append(f"- line {c['line']}: {c['code']}")
    else:
        result.append("- none")

    result.append("")

    # -----------------------
    # SEQUENCE
    # -----------------------
    result.append("🔁 SEQUENCE:")
    for s in flow.get("sequence", []):
        result.append(f"- line {s['line']}: {s['code']}")

    # -----------------------
    # SUMMARY
    # -----------------------
    result.append("")
    result.append("=== SUMMARY ===")

    if flow.get("writes"):
        result.append("STATUS: FIELD IS WRITTEN")
    elif flow.get("reads"):
        result.append("STATUS: FIELD IS ONLY READ")
    else:
        result.append("STATUS: FIELD NOT USED")

    return "\n".join(result)