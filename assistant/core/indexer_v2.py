import os
import re
import json

print("\n[INDEXER] START")

# =========================
# ROOT DETECTION
# =========================
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

print("[TEST] PROJECT_ROOT =", PROJECT_ROOT)

if not os.path.exists(PROJECT_ROOT):
    print("[ERROR] PROJECT_ROOT DOES NOT EXIST")
    exit()

# =========================
# OUTPUT
# =========================
INDEX_DIR = os.path.join(PROJECT_ROOT, "assistant/index")
INDEX_FILE = os.path.join(INDEX_DIR, "index.json")

os.makedirs(INDEX_DIR, exist_ok=True)

print("[TEST] INDEX_DIR =", INDEX_DIR)

# =========================
# PATTERNS
# =========================
CLASS_RE = re.compile(r"class\s+(\w+)")
METHOD_RE = re.compile(r"function\s+(\w+)")
READ_HINT = "$"

WRITE_PATTERNS = [
    r"\$this->\w+->save",
    r"->save\(",
    r"->saveField\("
]


# =========================
# FILE SCANNER (V10 FIX)
# =========================
def scan_file(path):
    try:
        with open(path, "r", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        print("[SKIP FILE]", path, e)
        return []

    classes = []
    methods = []
    reads = []
    writes = []

    current_class = None
    current_method = None

    for i, line in enumerate(lines):

        # CLASS DETECT
        c = CLASS_RE.search(line)
        if c:
            current_class = c.group(1)
            classes.append(current_class)

        # METHOD DETECT
        m = METHOD_RE.search(line)
        if m:
            current_method = m.group(1)
            methods.append(current_method)

        # READ DETECT
        if READ_HINT in line:
            reads.append({
                "line": i + 1,
                "code": line.strip(),
                "class": current_class,
                "method": current_method
            })

        # WRITE DETECT
        for p in WRITE_PATTERNS:
            if re.search(p, line):
                writes.append({
                    "line": i + 1,
                    "code": line.strip(),
                    "class": current_class,
                    "method": current_method
                })

    # ignore empty files
    if not (classes or methods or reads or writes):
        return []

    # build symbol entries
    symbols = []

    # create symbol nodes for methods
    for cls in classes:
        for method in methods:

            sym_reads = [
                r for r in reads
                if r["class"] == cls and r["method"] == method
            ]

            sym_writes = [
                w for w in writes
                if w["class"] == cls and w["method"] == method
            ]

            symbols.append({
                "file": path,
                "class": cls,
                "method": method,
                "reads": sym_reads,
                "writes": sym_writes
            })

    return symbols


# =========================
# BUILD INDEX
# =========================
def build_index(root):
    index = []
    total_files = 0
    matched = 0

    for dirpath, _, files in os.walk(root):
        for file in files:

            if file.startswith("."):
                continue

            if not file.endswith((".php", ".ctp")):
                continue

            full_path = os.path.join(dirpath, file)

            total_files += 1

            result = scan_file(full_path)

            if result:
                index.extend(result)
                matched += 1

                print(f"[SCAN] {file} -> {len(result)} symbols")

    print("\n[STATS]")
    print("TOTAL FILES:", total_files)
    print("MATCHED FILES:", matched)
    print("TOTAL SYMBOLS:", len(index))

    return index


# =========================
# MAIN
# =========================
def main():
    index = build_index(PROJECT_ROOT)

    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)

    print("\n[WRITE]", INDEX_FILE)
    print("[INDEX SIZE]", len(index))
    print("[INDEXER] DONE\n")


if __name__ == "__main__":
    main()