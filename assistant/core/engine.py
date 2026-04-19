import os
import re

from core.search import find_target
from core.model import call_model
from core.analyzer import find_field_flow, find_request_input
from core.context import extract_field as fallback_field
from core.global_search import search_field_in_project

from core.index_store import IndexStore
from core.lifecycle_engine import build_lifecycle

from proof.tracer import build_proof
from proof.global_tracer import build_global_report

from utils import load_prompt, log_time
from config import *


# =========================
# QUERY PARSER
# =========================
def parse_query(query):
    tokens = query.split()

    controller = None
    action = None
    field = None

    for t in tokens:

        if "Controller" in t:
            controller = t

        elif t.startswith("admin_"):
            action = t

        elif t in ["grand_total", "total", "type_id"]:
            field = t

        elif "_" in t and not t.startswith("admin_"):
            field = t

    return controller, action, field


# =========================
# AUTO FIELD DETECTOR 🔥
# =========================
def extract_fields_from_code(code):
    """
    V11.1 SMART FIELD DETECTOR

    приоритет:
    1. request->data
    2. переменные ($total)
    3. массивы ['total']
    """

    import re

    if not code:
        return []

    # =========================
    # 1. REQUEST (TOP PRIORITY)
    # =========================
    request_fields = re.findall(
        r"request->data\[['\"]([a-zA-Z0-9_]+)['\"]\]",
        code,
        re.IGNORECASE
    )

    if request_fields:
        return request_fields[:3]

    # =========================
    # 2. VARIABLES ($total)
    # =========================
    vars_found = re.findall(r"\$([a-zA-Z_][a-zA-Z0-9_]*)", code)

    priority_vars = [
        v for v in vars_found
        if v not in ["this", "data", "rs", "item"]
        and len(v) > 3
    ]

    if priority_vars:
        return priority_vars[:3]

    # =========================
    # 3. ARRAY KEYS
    # =========================
    keys_found = re.findall(r"\[['\"]([a-zA-Z0-9_]+)['\"]\]", code)

    priority_keys = [
        k for k in keys_found
        if len(k) > 4
        and k not in ["id", "name", "type"]
    ]

    return priority_keys[:3]

# =========================
# INDEX LOADER
# =========================
def load_index():
    index_path = os.path.join("assistant/index", "index.json")
    store = IndexStore(index_path)
    store.load()
    return store


# =========================
# ENGINE (V11 AUTO FIELD)
# =========================
def run_engine(query, prompt_override=None):

    start = log_time("START")

    index_store = load_index()

    controller, action, field = parse_query(query)

    # =========================
    # FIELD RESOLUTION
    # =========================
    if not field:
        field = fallback_field(query)

    # ❗ если поле совпадает с методом — сбрасываем
    if field == action:
        field = None

    print(f"[CONTROLLER] {controller}")
    print(f"[ACTION] {action}")
    print(f"[FIELD] {field}")

    # =========================
    # CLEAN INDEX
    # =========================
    clean_index = []
    for x in index_store.data:
        if not isinstance(x, dict):
            continue

        x["reads"] = x.get("reads") or []
        x["writes"] = x.get("writes") or []

        clean_index.append(x)

    target = find_target(
        clean_index,
        controller if controller else query,
        action
    )

    # =========================
    # GLOBAL MODE
    # =========================
    if not target:

        print("[MODE] global")

        if not field:
            print("FIELD NOT FOUND")
            return

        results = index_store.find_field(field)

        if not results:
            results = search_field_in_project(PROJECT_ROOT, field)

        report = build_global_report(results, limit=40)

        print("\n--- GLOBAL SEARCH ---\n")
        print(report)
        return

    # =========================
    # LOCAL MODE
    # =========================
    print(f"[FOUND] {target.get('class')}::{target.get('method')}")

    with open(target["file"], "r", errors="ignore") as f:
        code = f.read()

    # =========================
    # 🔥 AUTO FIELD DETECT
    # =========================
    if not field:
        detected_fields = extract_fields_from_code(code)

        if detected_fields:
            field = detected_fields[0]
            print(f"[AUTO FIELD] {field}")
        else:
            field = "unknown_field"

    # =========================
    # FLOW
    # =========================
    flow = find_field_flow(code, field)

    if not isinstance(flow, dict):
        flow = {
            "reads": [],
            "writes": [],
            "conditions": [],
            "calls": [],
            "sequence": []
        }

    inputs = find_request_input(code, field)

    proof = build_proof(flow, field, inputs)

    print("\n--- PROOF ---\n", proof)

    # =========================
    # GLOBAL CONTEXT
    # =========================
    global_results = index_store.find_field(field)

    if not global_results:
        global_results = search_field_in_project(PROJECT_ROOT, field)

    global_report = build_global_report(global_results, limit=40)

    # =========================
    # MODE
    # =========================
    write_count = len(flow.get("writes", []) or [])
    input_missing = not inputs

    need_deep = input_missing or (write_count == 0)
    mode = "deep" if need_deep else "fast"

    print(f"[MODE] {mode}")

    # =========================
    # PROMPT
    # =========================
    prompt_file = prompt_override or "assistant/prompts/flow.txt"

    context = proof

    if mode == "deep":
        if global_report:
            context += "\n\n--- GLOBAL ---\n" + global_report

        if len(flow.get("reads", [])) < 5:
            context += "\n\n--- CODE ---\n" + code[:800]

    prompt = load_prompt(prompt_file).format(
        context=context,
        query=query,
        var=field
    )

    t = log_time("LLM")

    result = call_model(
        FAST_MODEL if mode == "fast" else DEEP_MODEL,
        prompt,
        FAST_TOKENS if mode == "fast" else DEEP_TOKENS,
        120 if mode == "fast" else 300
    )

    log_time("LLM", t)

    if not result and RETRY_ON_EMPTY:
        print("[RETRY]")
        result = call_model(DEEP_MODEL, prompt, DEEP_TOKENS, 300)

    print("\n--- RESULT ---\n")
    print(result or "нет ответа")

    log_time("TOTAL", start)

    # =========================
    # LIFECYCLE
    # =========================
    lifecycle = build_lifecycle(flow, field)

    print("\n--- FIELD LIFECYCLE ---\n")
    print("READS:", len(lifecycle.reads))
    print("WRITES:", len(lifecycle.writes))
    print("TRANSFORMS:", len(lifecycle.transforms))
    print("RENDERS:", len(lifecycle.renders))
    print("EXPORTS:", len(lifecycle.exports))
    print("STATUS:", lifecycle.status())