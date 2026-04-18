import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSISTANT_DIR = os.path.join(BASE_DIR, "assistant")

if ASSISTANT_DIR not in sys.path:
    sys.path.insert(0, ASSISTANT_DIR)

from core.engine import run_engine
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str)
    parser.add_argument("--prompt", type=str, default=None)

    args = parser.parse_args()

    run_engine(args.query, args.prompt)