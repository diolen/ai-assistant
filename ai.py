import sys
import os
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSISTANT_DIR = os.path.join(BASE_DIR, "assistant")

if ASSISTANT_DIR not in sys.path:
    sys.path.insert(0, ASSISTANT_DIR)

from core.engine import run_engine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str)
    parser.add_argument("--prompt", type=str, default=None)

    args = parser.parse_args()

    # =========================
    # PURE ENTRY POINT (V10.3.2)
    # =========================
    run_engine(args.query, args.prompt)


if __name__ == "__main__":
    main()