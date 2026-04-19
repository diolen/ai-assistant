# core/field_classifier.py


def _normalize(code):
    if not isinstance(code, str):
        return ""
    return code.lower()


def _has_field(code, field):
    code_l = _normalize(code)
    field_l = field.lower()

    # защита от подстрок (id vs order_id)
    return (
        f"{field_l}" in code_l
    )


# =========================
# TRANSFORM
# =========================
def is_transform(code, field):
    code_l = _normalize(code)

    if not _has_field(code_l, field):
        return False

    return any(x in code_l for x in [
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
# RENDER (VIEW OUTPUT)
# =========================
def is_render(code, field):
    code_l = _normalize(code)

    if not _has_field(code_l, field):
        return False

    return any(x in code_l for x in [
        "echo",
        "print",
        "number_format",
        "set(",            # CakePHP view set
        "setcompact",
        "render",
        "view"
    ])


# =========================
# EXPORT (FILE/API OUTPUT)
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
# WRITE (DATA PERSIST)
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
# READ (SAFE)
# =========================
def is_read(code, field):
    code_l = _normalize(code)

    if not _has_field(code_l, field):
        return False

    # READ = упоминание без записи
    if "=" in code_l:
        return False

    return True