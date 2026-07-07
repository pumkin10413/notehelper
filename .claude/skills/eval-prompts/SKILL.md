---
name: eval-prompts
description: Run the chart-quality regression eval, or improve prompts/templates in response to a bad chart output. Use after editing prompts or templates, when the user reports the generated chart was wrong, invented facts, or had bad formatting.
---

# Improve chart quality safely

## Just run the eval
```bash
python3 eval/run_eval.py     # 1-3 min; exit 0 = pass
```

## The user reported a bad output — fix loop
1. Reproduce: get the exact bullets and chart type; run `scripts/chart.py` and confirm the flaw.
2. Encode it as a new eval case in `eval/cases/` (must_contain / must_not_contain capturing
   the correct behavior). Run it — it should FAIL now. This proves the case detects the bug.
3. Fix at the right layer, in this order of preference:
   a. `templates/<type>.md` RULES section (local, safest),
   b. the skeleton itself,
   c. `prompts/system-chart.txt` (global — only for cross-type problems; keep < ~600 words;
      NEVER weaken the ABSOLUTE PROHIBITIONS block).
   Back up the file before editing (`cp X X.bak-$(date +%Y%m%d)`).
4. Run the FULL eval. New case passes + no old case broke = done. Anything broke = revert
   and try a smaller edit. Two failed attempts in a row → stop, write findings to
   docs/HANDOFF.md, and tell the user what you tried; don't churn.
5. Rules of the road: prompts/README.md. Never delete or weaken an eval case to make it pass.
