from core.lifecycle import FieldLifecycle
from core.field_classifier import *


def build_lifecycle(flow, field):
    """
    V12 LIFECYCLE ENGINE (STATE MACHINE FIXED)

    FIXES:
    - corrected DERIVED logic (was broken)
    - fixed conditions detection bug
    - aligned transforms/exports semantics
    - deterministic status resolution
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
                return {"line": item[0], "code": item[1]}
            return {"line": None, "code": str(item)}

        return {"line": None, "code": str(item)}

    def safe(name):
        return [normalize(x) for x in flow.get(name, []) if x]

    reads = safe("reads")
    writes = safe("writes")
    conditions = safe("conditions")
    calls = safe("calls")
    sequence = safe("sequence")

    # =========================
    # READ PHASE
    # =========================
    for r in reads:
        code = r.get("code", "")
        if field in code:
            lifecycle.add("READ", r)

            if is_transform(code, field):
                lifecycle.add("TRANSFORM", r)

            if is_render(code, field):
                lifecycle.add("RENDER", r)

            if is_export(code, field):
                lifecycle.add("EXPORT", r)

    # =========================
    # WRITE PHASE
    # =========================
    for w in writes:
        code = w.get("code", "")
        if field in code:
            lifecycle.add("WRITE", w)

            # semantic enrichment
            if "->set(" in code:
                lifecycle.add("TRANSFORM", w)

            if "save" in code.lower():
                lifecycle.add("EXPORT", w)

    # =========================
    # CONDITIONS (FIXED BUG)
    # =========================
    for c in conditions:
        code = c.get("code", "")
        if field in code:
            lifecycle.add("CONDITION", c)

    # =========================
    # CALLS
    # =========================
    for c in calls:
        code = c.get("code", "")
        if field in code:
            lifecycle.add("CALL", c)

    # =========================
    # SEQUENCE
    # =========================
    for s in sequence:
        code = s.get("code", "")
        if field in code:
            lifecycle.add("SEQUENCE", s)

    # =========================
    # METRICS
    # =========================
    has_reads = len(lifecycle.reads) > 0
    has_writes = len(lifecycle.writes) > 0
    has_transform = len(lifecycle.transforms) > 0
    has_export = len(lifecycle.exports) > 0
    has_render = len(lifecycle.renders) > 0
    has_conditions = len(lifecycle.conditions) > 0   # ❗ FIXED (was derivations bug)

    # =========================
    # STATE MACHINE (CLEAN)
    # =========================

    if has_writes and has_export:
        status = "PERSISTED_AND_EXPORTED_FIELD"

    elif has_writes and has_transform:
        status = "TRANSFORMED_FIELD"

    elif has_writes:
        status = "MUTATED_FIELD"

    elif has_reads and has_conditions:
        status = "DERIVED_FIELD"

    elif has_reads:
        status = "READONLY_FIELD"

    else:
        status = "UNUSED_FIELD"

    lifecycle._status = status
    lifecycle.status = lambda: lifecycle._status

    return lifecycle