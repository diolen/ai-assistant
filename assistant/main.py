import sys
from core.engine import run_engine
from core.indexer import index_project, save_index

def run_assistant():

    if "--index" in sys.argv:
        print("[INDEX] building project index...")
        index = index_project("./app")
        save_index(index)
        print("[INDEX] done")
        return

    if len(sys.argv) < 2:
        print("usage: python assistant.py 'query' [--prompt file]")
        return

    query = sys.argv[1]

    prompt_file = "debug.txt"

    if "--prompt" in sys.argv:
        i = sys.argv.index("--prompt")
        prompt_file = sys.argv[i + 1]

    run_engine(query, prompt_file)