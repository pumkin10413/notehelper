# Instructions for AI agents (Hermes, Gemini, Claude, any framework)

You are working in a **local medical charting assistant** for a hospital resident. Read
[CLAUDE.md](CLAUDE.md) for the file map — it applies to you too, whatever your name is.

## Non-negotiable rules
1. Patient data never leaves this machine. Do not send chart text, transcripts, or samples to
   any web API or search. The local Ollama model (127.0.0.1:11434) is the only model allowed
   to see chart content. Full rules: [docs/PHI-SAFETY.md](docs/PHI-SAFETY.md).
2. Before modifying an existing file: `cp <file> <file>.bak-$(date +%Y%m%d)` or make a git commit.
3. After changing anything in `prompts/` or `templates/`: run `python3 eval/run_eval.py`.
   If it exits nonzero, revert your change.
4. Keep all Python stdlib-only and Python-3.9 compatible (no `match` statements, no `int | None`).

## How to generate a chart (the main user-facing task)
```bash
# If anything errors, first run: bash scripts/doctor.sh   (it prints the fix)
python3 scripts/chart.py --type admission --bullets "<the user's bullet points>"
# types: admission | procedure | consult | progress   (files in templates/)
```
Or start the UI for the user: `python3 app/server.py` → http://127.0.0.1:8765

If YOU are a capable LLM and the user asks you to draft the chart directly instead of using
the local model: read `prompts/system-chart.txt` and the matching `templates/<type>.md`, follow
them exactly, and apply the same no-invented-facts rules. Only do this if the user pasted the
clinical content to you themselves.

## How to call the local model from any framework
Ollama exposes an OpenAI-compatible endpoint:
```
base_url = http://127.0.0.1:11434/v1     api_key = "ollama" (any string)
model    = qwen2.5:7b-instruct           temperature = 0.2
system   = contents of prompts/system-chart.txt
user     = "TEMPLATE:\n<templates/TYPE.md>\n\nPHYSICIAN INPUT:\n<bullets>"
```

## Task recipes
| User says | Do |
|---|---|
| "chart this / make an admission note" | recipe above; show output; remind user to proofread |
| "it keeps writing X wrong" | edit that template's RULES section (backup first), add an eval case reproducing it, run eval |
| "whisper mishears <term>" | append `wrong => right` to `prompts/vocab-corrections.txt` (rules in prompts/README.md) |
| "add my hospital's format" | follow the procedure in `templates/README.md` — de-identify FIRST |
| "something is broken" | `bash scripts/doctor.sh`, then the table in docs/ARCHITECTURE.md |
| "update the handoff" | append to `docs/HANDOFF.md` using its session-entry format |
