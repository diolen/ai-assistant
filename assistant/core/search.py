def find_target(index, controller_query, action=None):
    """
    V11 TARGET RESOLVER (STRICT + SAFE MATCHING)

    FIXES:
    - no substring controller match
    - strict controller normalization
    - method scoped to controller
    - removes weak false positives
    """

    if not controller_query or not index:
        return None

    q = controller_query.strip().lower()
    action_l = action.strip().lower() if action else None

    exact_match = None
    method_match = None
    class_match = None

    def norm(s):
        return (s or "").strip().lower()

    for item in index:

        if not isinstance(item, dict):
            continue

        class_name = item.get("class") or ""
        method = item.get("method") or ""
        file = item.get("file")

        class_l = norm(class_name)
        method_l = norm(method)

        if not class_l:
            continue

        # =========================
        # 1. EXACT MATCH (HIGHEST PRIORITY)
        # =========================
        if action_l and class_l == q and method_l == action_l:
            return {
                "file": file,
                "class": class_name,
                "method": method
            }

        # =========================
        # 2. METHOD MATCH (BUT ONLY IF CONTROLLER MATCHES EXACTLY OR NOT SET YET)
        # =========================
        if action_l and method_l == action_l and class_l == q:
            method_match = {
                "file": file,
                "class": class_name,
                "method": method
            }

        # =========================
        # 3. CLASS MATCH (STRICT ONLY)
        # =========================
        if class_l == q and not class_match:
            class_match = {
                "file": file,
                "class": class_name,
                "method": method
            }

    # =========================
    # FINAL DECISION TREE
    # =========================
    return (
        method_match
        or class_match
    )