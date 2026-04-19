import time
import os

# =========================
# INTERNAL CACHE (CRITICAL SPEEDUP)
# =========================
_PROMPT_CACHE = {}

# =========================
# LOGGER (LIGHTWEIGHT)
# =========================
def log_time(label, start=None, enabled=True):
    """
    V10.3.3:
    - можно отключить логирование
    - быстрее форматирование
    """

    if not enabled:
        return time.time() if not start else None

    if not start:
        t = time.time()
        print(f"[{label}] start {time.strftime('%H:%M:%S')}")
        return t
    else:
        diff = time.time() - start
        print(f"[{label}] done ({round(diff, 2)}s)")


# =========================
# PROMPT LOADER (CACHED)
# =========================
def load_prompt(path):
    """
    V10.3.3:
    - кеширует промпты (огромный буст)
    - безопасная загрузка
    """

    if not path:
        return ""

    # =========================
    # CACHE HIT
    # =========================
    if path in _PROMPT_CACHE:
        return _PROMPT_CACHE[path]

    # =========================
    # SAFE LOAD
    # =========================
    if not os.path.exists(path):
        print(f"[PROMPT ERROR] file not found: {path}")
        return ""

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            _PROMPT_CACHE[path] = content
            return content
    except Exception as e:
        print(f"[PROMPT ERROR] {e}")
        return ""