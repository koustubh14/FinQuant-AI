"""Profile actual local snapshot replay; no provider or LLM calls."""

import cProfile
import io
import json
import pstats
import time
from pathlib import Path

from replay import replay

root = Path(__file__).resolve().parents[1]
profile = cProfile.Profile()
started = time.perf_counter()
profile.enable()
result = replay(root / "data/examples/AAPL.json")
profile.disable()
elapsed = time.perf_counter() - started
output = io.StringIO()
pstats.Stats(profile, stream=output).sort_stats("cumulative").print_stats(18)
(root / "docs/results/profile.txt").write_text(output.getvalue(), encoding="utf-8")
print(json.dumps({"replay_seconds": elapsed, "result": result}, indent=2))
