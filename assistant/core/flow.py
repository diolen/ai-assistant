import re


def build_flow(code: str, field: str):
    """
    V10 FLOW ENGINE (lightweight semantic flow)
    """
    if not code:
        return {
            "reads": [],
            "writes": [],
            "conditions": [],
            "calls": [],
            "sequence": []
        }    

    lines = code.split("\n")

    flow = {
        "reads": [],
        "writes": [],
        "conditions": [],
        "calls": [],
        "sequence": []
    }

    for i, line in enumerate(lines):

        lower = line.lower()

        # -----------------------
        # READ
        # -----------------------
        if f"['{field}']" in line or f'["{field}"]' in line:
            flow["reads"].append({
                "line": i + 1,
                "code": line.strip()
            })

        # -----------------------
        # WRITE (save / set)
        # -----------------------
        if "save(" in lower or "savefield" in lower or f"set('{field}'" in lower:
            flow["writes"].append({
                "line": i + 1,
                "code": line.strip()
            })

        # -----------------------
        # CONDITIONS
        # -----------------------
        if "if(" in lower or "elseif" in lower:
            flow["conditions"].append({
                "line": i + 1,
                "code": line.strip()
            })

        # -----------------------
        # MODEL / METHOD CALLS
        # -----------------------
        if "->" in line and "(" in line:
            flow["calls"].append({
                "line": i + 1,
                "code": line.strip()
            })

    # -----------------------
    # SIMPLE FLOW ORDERING
    # -----------------------

    flow["sequence"] = sorted(
        flow["reads"] + flow["conditions"] + flow["writes"] + flow["calls"],
        key=lambda x: x["line"]
    )

    return flow