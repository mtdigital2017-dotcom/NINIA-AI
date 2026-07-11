#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dt_runtime.orchestrator import DTRuntimeOrchestrator

def main() -> int:
    parser = argparse.ArgumentParser(description="NINIA DT Runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("refresh", help="Reconstruye el contexto actual")
    sub.add_parser("status", help="Muestra el contexto actual")
    review = sub.add_parser("review", help="Revisa una propuesta antes de implementarla")
    review.add_argument("proposal")
    review.add_argument("--manual", action="store_true")
    args = parser.parse_args()
    runtime = DTRuntimeOrchestrator(ROOT)
    if args.command in {"refresh", "status"}:
        result = runtime.refresh()
    else:
        result = runtime.review(args.proposal, args.manual)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("qa", result.get("context", {}).get("qa", {})).get("valid", True) else 1

if __name__ == "__main__":
    raise SystemExit(main())
