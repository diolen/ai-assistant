def find_target(index, controller_query, action=None):
    """
    V10.9 TARGET RESOLVER (HARD PRIORITY)

    FIXES:
    - строгий приоритет controller + action
    - защита от beforeFilter
    - детерминированный выбор (без перезаписи)
    """

    if not controller_query or not index:
        return None

    q = controller_query.lower().strip()
    action_l = action.lower().strip() if action else None

    exact_match = None
    method_match = None
    class_match = None
    weak_match = None

    for item in index:

        if not isinstance(item, dict):
            continue

        class_name = (item.get("class") or "").strip()
        method = (item.get("method") or "").strip()
        file = item.get("file")

        if not class_name and not method:
            continue

        class_l = class_name.lower()
        method_l = method.lower()

        # =========================
        # 1. EXACT controller + action (ТОП ПРИОРИТЕТ)
        # =========================
        if action_l and class_l == q and method_l == action_l:
            exact_match = {
                "file": file,
                "class": class_name,
                "method": method
            }
            break  # 🔥 сразу выходим

        # =========================
        # 2. METHOD ONLY (если совпал action)
        # =========================
        if action_l and method_l == action_l and not method_match:
            method_match = {
                "file": file,
                "class": class_name,
                "method": method
            }

        # =========================
        # 3. CLASS ONLY (но не beforeFilter)
        # =========================
        if class_l == q and method_l != "beforefilter" and not class_match:
            class_match = {
                "file": file,
                "class": class_name,
                "method": method
            }

        # =========================
        # 4. WEAK MATCH
        # =========================
        if not weak_match and (q in class_l or (action_l and action_l in method_l)):
            weak_match = {
                "file": file,
                "class": class_name,
                "method": method
            }

    # =========================
    # FINAL PRIORITY
    # =========================
    return (
        exact_match
        or method_match
        or class_match
        or weak_match
    )