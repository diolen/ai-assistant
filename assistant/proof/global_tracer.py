from collections import defaultdict
from assistant.utils.colors import Color, c


def detect_group(path):
    if not path:
        return "OTHER"

    if "/Model/" in path:
        return "MODEL"
    elif "/Controller/" in path:
        return "CONTROLLER"
    elif "/View/" in path:
        return "VIEW"
    else:
        return "OTHER"


def detect_type(code):
    if not isinstance(code, str):
        return "READ"

    code_l = code.lower()

    # ❗ FIX: убрали "=" как признак WRITE
    if "save(" in code_l or "->save(" in code_l or "set(" in code_l:
        return "WRITE"

    if "if" in code_l or "elseif" in code_l:
        return "CONDITION"

    return "READ"


def _shorten(code, max_len=140):
    """
    ❗ критично для LLM
    режем длинные строки
    """
    if not isinstance(code, str):
        return ""

    code = code.strip()

    if len(code) <= max_len:
        return code

    return code[:max_len] + " ..."


def build_global_report(results, filter_type=None, grep=None, limit=120):
    """
    V10.3.3 OPTIMIZED GLOBAL REPORT

    FIXES:
    - жесткий лимит строк
    - обрезка кода
    - меньше мусора → быстрее LLM
    """

    if not results:
        return "NO GLOBAL DATA"

    grouped = defaultdict(list)

    # =========================
    # PRE-FILTER
    # =========================
    for r in results:

        if not isinstance(r, dict):
            continue

        code = r.get("code", "")
        file = r.get("file", "")

        usage = detect_type(code)

        if filter_type and usage != filter_type:
            continue

        if grep and grep.lower() not in code.lower():
            continue

        group = detect_group(file)

        grouped[group].append({
            "file": file,
            "line": r.get("line"),
            "code": _shorten(code),
            "usage": usage
        })

    # =========================
    # BUILD OUTPUT
    # =========================
    out = []
    total = 0

    # ❗ приоритет групп
    ordered_groups = ["CONTROLLER", "MODEL", "VIEW", "OTHER"]

    for group in ordered_groups:

        items = grouped.get(group)
        if not items:
            continue

        out.append(c(f"\n=== {group} ({len(items)}) ===", Color.BLUE))

        for r in items:

            if total >= limit:
                out.append(c("\n[TRUNCATED GLOBAL OUTPUT]", Color.RED))
                out.append(c(f"[TOTAL SHOWN] {total}", Color.GREEN))
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

            total += 1

    out.append(c(f"\n[TOTAL SHOWN] {total}", Color.GREEN))

    return "\n".join(out)