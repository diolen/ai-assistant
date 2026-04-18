def find_target(index, query):
    q = query.lower()

    best = None

    for item in index:
        class_match = item["class"].lower() in q
        method_match = item["method"].lower() in q

        # идеальный матч
        if class_match and method_match:
            return item

        # запасной вариант
        if method_match and not best:
            best = item

    return best