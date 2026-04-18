import time

def log_time(label, start=None):
    if not start:
        t = time.time()
        print(f"[{label}] start {time.strftime('%H:%M:%S')}")
        return t
    else:
        diff = time.time() - start
        print(f"[{label}] done ({round(diff,2)}s)")

def load_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()