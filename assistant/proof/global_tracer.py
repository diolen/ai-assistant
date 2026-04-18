from collections import defaultdict
from assistant.utils.colors import Color, c


def detect_group(path):
    if "/Model/" in path:
        return "MODEL"
    elif "/Controller/" in path:
        return "CONTROLLER"
    elif "/View/" in path:
        return "VIEW"
    else:
        return "OTHER"


def detect_type(code):
    code_l = code.lower()

    if "save" in code_l or "set(" in code_l or "=" in code_l:
        return "WRITE"
    elif "if" in code_l or "elseif" in code_l:
        return "CONDITION"
    else:
        return "READ"


def build_global_report(results, filter_type=None, grep=None, limit=None):
    grouped = defaultdict(list)

    for r in results:
        r["group"] = detect_group(r["file"])
        r["usage"] = detect_type(r["code"])

        if filter_type and r["usage"] != filter_type:
            continue

        if grep and grep.lower() not in r["code"].lower():
            continue

        grouped[r["group"]].append(r)

    out = []

    total = 0

    for group, items in grouped.items():
        if not items:
            continue

        # заголовок группы
        out.append(c(f"\n=== {group} ({len(items)}) ===", Color.BLUE))

        for r in items:
            total += 1

            if limit and total > limit:
                out.append(c("\n[TRUNCATED]", Color.RED))
                return "\n".join(out)

            usage_color = {
                "WRITE": Color.YELLOW,
                "READ": Color.GREEN,
                "CONDITION": Color.CYAN
            }.get(r["usage"], Color.GRAY)

            line = c(f"{r['file']}:{r['line']}", Color.GRAY)
            code = c(r["code"], usage_color)

            out.append(line)
            out.append(f"  {code}")

    out.append(c(f"\n[TOTAL SHOWN] {total}", Color.GREEN))

    return "\n".join(out)