from core.lifecycle import FieldLifecycle
from core.field_classifier import *


def build_lifecycle(flow, field):
    """
    V10.3.2 FINAL FIX:
    - uses FLOW instead of INDEX
    - normalizes tuples/dicts safely
    - fixes false DERIVED_FIELD issue
    """

    lifecycle = FieldLifecycle(field)

    if not flow:
        return lifecycle

    # =========================
    # NORMALIZER
    # =========================
    def normalize(item):
        if isinstance(item, dict):
            return item

        if isinstance(item, (list, tuple)):
            if len(item) >= 2:
                return {
                    "line": item[0],
                    "code": item[1]
                }
            return {
                "line": None,
                "code": str(item)
            }

        return {
            "line": None,
            "code": str(item)
        }

    def safe_list(name):
        data = flow.get(name, [])
        if not data:
            return []
        return [normalize(x) for x in data if x is not None]

    reads = safe_list("reads")
    writes = safe_list("writes")

    # legacy support (optional)
    conditions = safe_list("conditions")
    calls = safe_list("calls")
    sequence = safe_list("sequence")

    # =========================
    # READS
    # =========================
    for r in reads:
        code = r.get("code", "")
        if field and field in code:
            lifecycle.add("READ", r)

            if is_transform(code, field):
                lifecycle.add("TRANSFORM", r)

            if is_render(code, field):
                lifecycle.add("RENDER", r)

            if is_export(code, field):
                lifecycle.add("EXPORT", r)

    # =========================
    # WRITES
    # =========================
    for w in writes:
        code = w.get("code", "")
        if field and field in code:
            lifecycle.add("WRITE", w)

    # =========================
    # OPTIONAL SIGNALS (ENRICHMENT)
    # =========================
    for c in conditions:
        if field in c.get("code", ""):
            lifecycle.add("CONDITION", c)

    for c in calls:
        if field in c.get("code", ""):
            lifecycle.add("CALL", c)

    for s in sequence:
        if field in s.get("code", ""):
            lifecycle.add("SEQUENCE", s)

    return lifecycle