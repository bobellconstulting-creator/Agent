import argparse
import time

from agent.manager import run_once
from agent.store import init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BuckGrid worker loop")
    parser.add_argument("--loop", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=float, default=2.0, help="Loop interval seconds")
    args = parser.parse_args()

    init_db()

    if args.loop:
        while True:
            run_once()
            time.sleep(args.interval)
    else:
        print(run_once())


if __name__ == "__main__":
    main()
