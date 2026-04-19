# core/lifecycle.py

class FieldLifecycle:
    def __init__(self, field):
        self.field = field

        self.reads = []
        self.writes = []

        self.transforms = []
        self.derivations = []

        self.renders = []
        self.exports = []

    def add(self, kind, item):
        if kind == "READ":
            self.reads.append(item)

        elif kind == "WRITE":
            self.writes.append(item)

        elif kind == "TRANSFORM":
            self.transforms.append(item)

        elif kind == "DERIVED":
            self.derivations.append(item)

        elif kind == "RENDER":
            self.renders.append(item)

        elif kind == "EXPORT":
            self.exports.append(item)

    def status(self):
        """
        V10.7 FINAL LOGIC

        PRIORITY:
        1. STORED_FIELD — есть запись
        2. DERIVED_FIELD — есть трансформация
        3. OUTPUT_FIELD — только выводится
        4. READONLY_FIELD — только читается
        5. UNUSED — нигде нет
        """

        # =========================
        # STORED (самый важный)
        # =========================
        if self.writes:
            return "STORED_FIELD"

        # =========================
        # DERIVED (реальные вычисления)
        # =========================
        if self.transforms or self.derivations:
            return "DERIVED_FIELD"

        # =========================
        # OUTPUT (рендер / экспорт)
        # =========================
        if self.renders or self.exports:
            return "OUTPUT_FIELD"

        # =========================
        # READ ONLY
        # =========================
        if self.reads:
            return "READONLY_FIELD"

        # =========================
        # UNUSED
        # =========================
        return "UNUSED"