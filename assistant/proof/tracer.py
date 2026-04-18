def build_proof(flow, field, inputs):

    out = []

    if not inputs:
        out.append("⚠ INPUT отсутствует")

    if flow["reads"]:
        out.append("READ:")
        for i, l in flow["reads"]:
            out.append(f"{i}: {l}")

    if flow["writes"]:
        out.append("WRITE:")
        for i, l in flow["writes"]:
            out.append(f"{i}: {l}")
    else:
        out.append("⚠ WRITE отсутствует")

    if flow["writes"] and not flow.get("saves"):
        out.append("⚠ SET БЕЗ SAVE")        

    if not flow.get("saves"):
        out.append("⚠ SAVE отсутствует")

    return "\n".join(out)