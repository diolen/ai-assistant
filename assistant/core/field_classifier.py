# core/field_classifier.py

import re


def _normalize(code):
    if not isinstance(code, str):
        return ""
    return code.lower()


# =========================
# STRICT FIELD MATCH (FIXED)
# =========================
def _has_field(code, field):
    code_l = _normalize(code)
    field_l = field.lower()

    # word boundary protection (FIX)
    pattern = rf"\b{re.escape(field_l)}\b"
    return re.search(pattern, code_l) is not None


# =========================
# TRANSFORM
# =========================
def is_transform(code, field):
    code_l = _normalize(code)

    if not _has_field(code_l, field):
        return False

    return any(op in code_l for op in [
        "+=",
        "-=",
        "*=",
        "/=",
        "array_sum",
        "count(",
        "foreach",
        "map(",
        "reduce",
        "round(",
        "ceil(",
        "floor("
    ])


# =========================
# RENDER
# =========================
def is_render(code, field):
    code_l = _normalize(code)

    if not _has_field(code_l, field):
        return False

    return any(x in code_l for x in [
        "echo",
        "print",
        "number_format",
        "set(",
        "render",
        "view"
    ])


# =========================
# EXPORT
# =========================
def is_export(code, field):
    code_l = _normalize(code)

    if not _has_field(code_l, field):
        return False

    return any(x in code_l for x in [
        "csv",
        "excel",
        "xlsx",
        "fputcsv",
        "php://output",
        "download",
        "export"
    ])


# =========================
# WRITE (PRIORITY FIX)
# =========================
def is_write(code, field):
    code_l = _normalize(code)

    if not _has_field(code_l, field):
        return False

    return any(x in code_l for x in [
        "->set(",
        "->save",
        "insert",
        "update",
        "patchentity",
        "newentity"
    ])


# =========================
# READ (FIXED LOGIC)
# =========================
def is_read(code, field):
    code_l = _normalize(code)

    if not _has_field(code_l, field):
        return False

    # ❗ write has priority over read
    if is_write(code_l, field):
        return False

    return True