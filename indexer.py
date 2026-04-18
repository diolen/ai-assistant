import os
import re
import json

PROJECT_ROOT = "./app"
OUTPUT_FILE = "assistant.json"

def scan():
    index = []

    class_re = re.compile(r'class\s+(\w+)')
    method_re = re.compile(r'function\s+(\w+)')

    for root, _, files in os.walk(PROJECT_ROOT):
        for f in files:
            if not f.endswith("Controller.php"):
                continue

            path = os.path.join(root, f)

            try:
                content = open(path, "r", encoding="utf-8", errors="ignore").read()
            except:
                continue

            c = class_re.search(content)
            if not c:
                continue

            class_name = c.group(1)
            methods = method_re.findall(content)

            for m in methods:
                index.append({
                    "class": class_name,
                    "method": m,
                    "file": path
                })

    return index

def main():
    data = scan()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"OK → {OUTPUT_FILE} ({len(data)} methods)")

if __name__ == "__main__":
    main()