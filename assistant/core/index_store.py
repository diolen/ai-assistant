import json
import os

class IndexStore:
    def __init__(self, path):
        self.path = path
        self.data = []

    def load(self):
        if not os.path.exists(self.path):
            print("[INDEX] NOT FOUND")
            self.data = []
            return

        with open(self.path, "r") as f:
            self.data = json.load(f)

        print(f"[INDEX] LOADED {len(self.data)} symbols")

    def raw(self):
        return self.data

    def find_field(self, field):
        """
        SYMBOL-BASED SEARCH (V10)
        """
        results = []

        for item in self.data:

            reads = item.get("reads", [])
            writes = item.get("writes", [])

            # search in reads
            for r in reads:
                if field in r.get("code", ""):
                    results.append({
                        "file": item.get("file"),
                        "class": item.get("class"),
                        "method": item.get("method"),
                        "line": r.get("line"),
                        "type": "READ",
                        "code": r.get("code")
                    })

            # search in writes
            for w in writes:
                if field in w.get("code", ""):
                    results.append({
                        "file": item.get("file"),
                        "class": item.get("class"),
                        "method": item.get("method"),
                        "line": w.get("line"),
                        "type": "WRITE",
                        "code": w.get("code")
                    })

        return results