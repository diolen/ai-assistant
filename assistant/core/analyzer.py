def find_field_flow(code, field):
    lines = code.split("\n")

    reads = []
    writes = []
    saves = []

    for i, line in enumerate(lines, 1):
        if field in line:
            if "set(" in line:
                writes.append((i, line.strip()))
            elif "save(" in line:
                saves.append((i, line.strip()))
            else:
                reads.append((i, line.strip()))

    return {
        "reads": reads,
        "writes": writes,
        "saves": saves
    }


def find_request_input(code, field):
    lines = code.split("\n")

    results = []

    for i, line in enumerate(lines, 1):
        if "request->data" in line and field in line:
            results.append((i, line.strip()))

    return results