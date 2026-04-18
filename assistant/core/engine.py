import os
import json

from core.search import find_target
from core.model import call_model
from core.analyzer import find_field_flow, find_request_input
from core.context import extract_field as fallback_field
from core.global_search import search_field_in_project

from core.index_store import IndexStore

from proof.tracer import build_proof
from proof.global_tracer import build_global_report

from utils import load_prompt, log_time
from config import *


# =========================
# QUERY PARSER (FIXED V10.2 CORE)
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
        elif t in ["grand_total", "total"] or "_" in t:
            field = t

    return controller, action, field


INTENTS = {
    "search": ["где", "найди", "используется"],
    "debug": ["почему", "ошибка", "баг", "не работает"],
    "flow": ["как проходит", "поток"],
    "refactor": ["исправь", "почини"]
}

PROMPT_MAP = {
    "search": "assistant/prompts/search.txt",
    "debug": "assistant/prompts/debug.txt",
    "flow": "assistant/prompts/flow.txt",
    "refactor": "assistant/prompts/refactor.txt"
}


def load_index():
    index_path = os.path.join("assistant/index", "index.json")
    index_store = IndexStore(index_path)
    index_store.load()
    return index_store


def run_engine(query, prompt_override=None):

    start = log_time("START")

    # =========================
    # LOAD INDEX
    # =========================
    index_store = load_index()

    # =========================
    # TARGET RESOLUTION
    # =========================
    target = find_target(index_store.raw(), query)

    # =========================
    # QUERY PARSING (FIXED)
    # =========================
    controller, action, field = parse_query(query)

    if not field:
        field = fallback_field(query)

    print(f"[CONTROLLER] {controller}")
    print(f"[ACTION] {action}")
    print(f"[FIELD] {field}")

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
            print("[INDEX MISS] fallback to global search")
            results = search_field_in_project(PROJECT_ROOT, field)

        report = build_global_report(results)

        print("\n--- GLOBAL SEARCH ---\n")
        print(report)

        return

    # =========================
    # LOCAL MODE
    # =========================
    print(f"[FOUND] {target['class']}::{target['method']}")

    with open(target["file"], "r", errors="ignore") as f:
        code = f.read()

    flow = find_field_flow(code, field)
    inputs = find_request_input(code, field)

    proof = build_proof(flow, field, inputs)

    print("\n--- PROOF ---\n", proof)

    # =========================
    # INDEX-FIRST GLOBAL VIEW
    # =========================
    global_results = index_store.find_field(field)

    if not global_results:
        global_results = search_field_in_project(PROJECT_ROOT, field)

    global_report = build_global_report(global_results)

    need_deep = not inputs or not flow["writes"]
    mode = "deep" if need_deep else "fast"

    print(f"[MODE] {mode}")

    final = []

    # FIX: correct iteration
    for intent in INTENTS.keys():

        prompt_file = prompt_override or PROMPT_MAP.get(intent)

        print(f"[STEP] {intent} → {prompt_file}")

        context = proof if mode == "fast" else (
            proof + "\n\n--- GLOBAL ---\n" +
            global_report + "\n\n--- CODE ---\n" +
            code[:2000]
        )

        prompt = load_prompt(prompt_file).format(
            context=context,
            query=query,
            var=field
        )

        t = log_time(intent.upper())

        res = call_model(
            FAST_MODEL if mode == "fast" else DEEP_MODEL,
            prompt,
            FAST_TOKENS if mode == "fast" else DEEP_TOKENS,
            60 if mode == "fast" else 300
        )

        log_time(intent.upper(), t)

        if not res and RETRY_ON_EMPTY:
            print("[RETRY]")
            res = call_model(DEEP_MODEL, prompt, DEEP_TOKENS, 300)

        final.append(f"\n=== {intent.upper()} ===\n{res or 'нет ответа'}")

    print("\n--- RESULT ---")
    print("\n".join(final))

    log_time("TOTAL", start)