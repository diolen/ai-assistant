import os
import re

from core.search import find_target
from core.model import call_model
from core.analyzer import find_field_flow, find_request_input
from core.context import extract_field as fallback_field, extract_nested_fields
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
# INDEX LOADER
# =========================
def load_index():
    index_path = os.path.join("assistant/index", "index.json")
    store = IndexStore(index_path)
    store.load()
    return store


# =========================
# ENGINE V11.3 STABLE
# =========================
def run_engine(query, prompt_override=None):

    start = log_time("START")

    index_store = load_index()

    controller, action, field = parse_query(query)

    # =========================
    # FIELD RESOLUTION (FIXED PRIORITY)
    # =========================
    if not field:
        field = fallback_field(query)

    # ❌ never allow action = field
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
        if isinstance(x, dict):
            x["reads"] = x.get("reads") or []
            x["writes"] = x.get("writes") or []
            clean_index.append(x)

    target = find_target(
        clean_index,
        controller if controller else query,
        action
    )

    # =========================
    # GLOBAL MODE (SAFE GATE)
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
    # 🔥 AUTO FIELD (ONLY IF STILL EMPTY)
    # =========================
    if not field:

        # 1. nested structured fields FIRST (IMPORTANT FIX)
        nested = extract_nested_fields(code)

        if nested:
            field = nested[0]
            print(f"[AUTO FIELD:NESTED] {field}")

        else:
            # 2. fallback heuristic
            detected = re.findall(r"\$([a-zA-Z_][a-zA-Z0-9_]*)", code)

            filtered = [
                v for v in detected
                if v not in {"this", "data", "rs", "item"}
                and len(v) > 3
            ]

            if filtered:
                field = filtered[0]
                print(f"[AUTO FIELD:VAR] {field}")
            else:
                field = "unknown_field"

    # =========================
    # FLOW ANALYSIS
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
    # MODE DECISION
    # =========================
    write_count = len(flow.get("writes", []))
    input_missing = not inputs

    need_deep = input_missing or (write_count == 0)
    mode = "deep" if need_deep else "fast"

    print(f"[MODE] {mode}")

    # =========================
    # PROMPT BUILD
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

    # =========================
    # LLM CALL
    # =========================
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