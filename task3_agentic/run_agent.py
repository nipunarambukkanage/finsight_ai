from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from src.agent import run_single_research, run_two_agent_research

parser = argparse.ArgumentParser()
parser.add_argument("--ticker", default="AAPL")
parser.add_argument("--two-agent", action="store_true")
parser.add_argument("--demo", action="store_true", help="Explicitly allow labelled deterministic fallback data")
args = parser.parse_args()
result = run_two_agent_research(args.ticker, allow_demo_fallback=args.demo) if args.two_agent else run_single_research(args.ticker, allow_demo_fallback=args.demo)
print(json.dumps(result.model_dump(), indent=2))
