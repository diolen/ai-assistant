class FieldLifecycle:
    def __init__(self, field):
        self.field = field

        self.reads = []
        self.writes = []

        self.transforms = []
        self.conditions = []   # ❗ FIX: добавили (у тебя раньше ломалась логика)
        self.calls = []

        self.renders = []
        self.exports = []

        self.sequence = []

        self._status = "UNUSED_FIELD"

    # =========================
    # ADD EVENT
    # =========================
    def add(self, kind, item):

        if kind == "READ":
            self.reads.append(item)

        elif kind == "WRITE":
            self.writes.append(item)

        elif kind == "TRANSFORM":
            self.transforms.append(item)

        elif kind == "CONDITION":   # ❗ FIX (важно для DERIVED_FIELD)
            self.conditions.append(item)

        elif kind == "CALL":
            self.calls.append(item)

        elif kind == "RENDER":
            self.renders.append(item)

        elif kind == "EXPORT":
            self.exports.append(item)

        elif kind == "SEQUENCE":
            self.sequence.append(item)

    # =========================
    # STATUS ENGINE (SYNC WITH V12 ENGINE)
    # =========================
    def status(self):

        has_reads = len(self.reads) > 0
        has_writes = len(self.writes) > 0
        has_transforms = len(self.transforms) > 0
        has_conditions = len(self.conditions) > 0
        has_exports = len(self.exports) > 0
        has_renders = len(self.renders) > 0

        # =========================
        # BIG TECH STATE MACHINE
        # =========================

        if has_writes and has_exports:
            self._status = "PERSISTED_AND_EXPORTED_FIELD"

        elif has_writes and has_transforms:
            self._status = "TRANSFORMED_FIELD"

        elif has_writes:
            self._status = "MUTATED_FIELD"

        elif has_reads and has_conditions:
            self._status = "DERIVED_FIELD"

        elif has_reads:
            self._status = "READONLY_FIELD"

        else:
            self._status = "UNUSED_FIELD"

        return self._status