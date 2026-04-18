from core.search import find_target
from core.model import call_model
from core.analyzer import find_field_flow, find_request_input
from core.context import extract_field as fallback_field
from core.global_search import search_field_in_project
from core.interpreter import interpret

from proof.tracer import build_proof
from proof.global_tracer import build_global_report

from utils import load_prompt, log_time
from config import *

import json

PROMPT_MAP = {
    "search": "assistant/prompts/search.txt",
    "debug": "assistant/prompts/debug.txt",
    "flow": "assistant/prompts/flow.txt",
    "refactor": "assistant/prompts/refactor.txt"
}

def load_index():
    with open(STRUCT_FILE) as f:
        return json.load(f)

def run_engine(query, prompt_override=None):

    start = log_time("START")

    index = load_index()
    target = find_target(index, query)

    if not target:
        print("[MODE] global")

        parsed = interpret(query)
        field = parsed["field"]

        if not field:
            field = fallback_field(query)

        if not field:
            print("FIELD NOT FOUND")
            return

        print(f"[FIELD] {field}")

        results = search_field_in_project(PROJECT_ROOT, field)

        report = build_global_report(
            results,
            filter_type=parsed.get("filter_type"),
            grep=parsed.get("grep"),
            limit=parsed.get("limit")
        )

        print("\n--- GLOBAL SEARCH ---\n")
        print(report)

        return

    print(f"[FOUND] {target['class']}::{target['method']}")

    parsed = interpret(query)
    intents = parsed["intents"]
    field = parsed["field"] or fallback_field(query) or "grand_total"

    print(f"[INTENTS] {intents}")
    print(f"[FIELD] {field}")

    with open(target["file"], "r", errors="ignore") as f:
        code = f.read()

    flow = find_field_flow(code, field)
    inputs = find_request_input(code, field)

    proof = build_proof(flow, field, inputs)

    print("\n--- PROOF ---\n", proof)

    global_results = search_field_in_project(PROJECT_ROOT, field)
    global_report = build_global_report(global_results)

    need_deep = not inputs or not flow["writes"]
    mode = "deep" if need_deep else "fast"

    print(f"[MODE] {mode}")

    final = []

    for intent in intents:

        prompt_file = prompt_override or PROMPT_MAP.get(intent, DEFAULT_PROMPT)

        print(f"[STEP] {intent} → {prompt_file}")

        context = proof if mode == "fast" else (
            proof + "\n\n--- GLOBAL ---\n" + global_report + "\n\n--- CODE ---\n" + code[:2000]
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