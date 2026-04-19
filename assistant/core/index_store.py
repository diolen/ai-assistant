import os
import json

from core.lifecycle_engine import build_lifecycle


class IndexStore:
    def __init__(self, path):
        self.path = path
        self.data = []

    def load(self):
        if not os.path.exists(self.path):
            print("[INDEX] NOT FOUND")
            self.data = []
            return

        try:
            with open(self.path, "r") as f:
                self.data = json.load(f)
        except Exception as e:
            print(f"[INDEX ERROR] {e}")
            self.data = []
            return

        print(f"[INDEX] LOADED {len(self.data)} symbols")

    def raw(self):
        return self.data

    def find_field(self, field):
        """
        V10.6 HARDENED:
        - safe for None
        - safe for corrupted index
        - case-insensitive search
        """

        if not field or not isinstance(field, str):
            return []

        field_l = field.lower()

        results = []

        for item in self.data:

            if not isinstance(item, dict):
                continue

            reads = item.get("reads") or []
            writes = item.get("writes") or []

            if not isinstance(reads, list):
                reads = []

            if not isinstance(writes, list):
                writes = []

            # =========================
            # READS
            # =========================
            for r in reads:

                if not isinstance(r, dict):
                    continue

                code = r.get("code")

                if not isinstance(code, str):
                    continue

                if field_l in code.lower():
                    results.append({
                        "file": item.get("file"),
                        "class": item.get("class"),
                        "method": item.get("method"),
                        "line": r.get("line"),
                        "type": "READ",
                        "code": code
                    })

            # =========================
            # WRITES
            # =========================
            for w in writes:

                if not isinstance(w, dict):
                    continue

                code = w.get("code")

                if not isinstance(code, str):
                    continue

                if field_l in code.lower():
                    results.append({
                        "file": item.get("file"),
                        "class": item.get("class"),
                        "method": item.get("method"),
                        "line": w.get("line"),
                        "type": "WRITE",
                        "code": code
                    })

        return results

    def build_field_lifecycle(self, field):
        return build_lifecycle(self.data, field)