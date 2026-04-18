import os

def search_field_in_project(root, field):
    results = []

    for path, _, files in os.walk(root):
        for f in files:
            if f.endswith(".php") or f.endswith(".ctp"):
                full = os.path.join(path, f)

                try:
                    with open(full, "r", errors="ignore") as file:
                        for i, line in enumerate(file, 1):
                            if field in line:
                                results.append({"file": full, "line": i, "code": line.strip()})
                except:
                    pass

    return results