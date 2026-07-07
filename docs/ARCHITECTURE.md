# Architecture & Design Decisions

## Data flow
```
 voice ──ffmpeg──▶ 16kHz wav ──whisper-cli──▶ transcript ──vocab_fix──▶ text
                                                                          │
 typed bullets ──────────────────────────────────────────────────────────┤
                                                                          ▼
                    templates/<type>.md + prompts/system-chart.txt ──▶ Ollama (local)
                                                                          │
                                                                          ▼
                                              formatted chart ──▶ user proofreads ──▶ EMR
```
Two equivalent front doors drive the same pipeline:
- **Web app** `app/server.py` (http://127.0.0.1:8765) — daily use.
- **CLI** `scripts/chart.py`, `scripts/dictate.sh`, `scripts/voice-chart.sh` — for agents
  (Claude Code, Hermes, Gemini) and scripting. The web server imports `scripts/chart.py`
  directly, so there is exactly ONE implementation of prompt-building and generation.

## Key decisions (and why — don't undo these casually)
1. **Stdlib-only Python, no venv, no pip.** System Python is 3.9; zero dependencies means the
   stack cannot rot and any agent can run it without environment setup. If you feel you need a
   package, first ask whether 30 lines of stdlib will do.
2. **Ollama over llama.cpp-direct or LM Studio.** One brew install, runs as a login service,
   stable localhost API that every agent framework speaks (also OpenAI-compatible at
   `http://127.0.0.1:11434/v1` — that is how Hermes/Gemini-driven tools should call it).
3. **Default chart model: `qwen2.5:7b-instruct`.** Chosen for strong instruction/format
   fidelity at 7B, no "thinking" output to strip, ~4.7 GB Q4 fits 16 GB RAM with headroom.
   Vetted alternatives if quality disappoints (pull-and-set `CHART_MODEL`, then run eval/):
   - `llama3.1:8b` — similar class, sometimes better prose.
   - `gemma3:4b` — much faster, use if latency annoys the user; expect more format slips.
   - Anything ≥ 12B: NOT on this 16 GB machine.
4. **whisper.cpp `small.en`.** English-only dictation (user's choice), small.en is the best
   accuracy/speed point on M3; `medium.en` is the documented upgrade path (SETUP.md).
5. **Templates and prompts are data, not code.** All chart-format knowledge lives in
   `templates/*.md` (per-type) and `prompts/system-chart.txt` (global). Improving chart output
   should almost always mean editing a template's RULES, not touching Python.
6. **Temperature 0.2.** This is format transformation; determinism beats creativity.
7. **Server binds 127.0.0.1 only** and there is no auth — acceptable ONLY because it never
   listens on the network. Never bind 0.0.0.0.
8. **No database.** Charts are transient: generated, proofread, pasted into the EMR, gone.
   Deliberate PHI-minimization — do not add history/persistence features without explicit
   user request and a PHI-SAFETY.md review.

## Failure modes & first moves
| Symptom | First move |
|---|---|
| Anything broken | `bash scripts/doctor.sh` — it names the fix |
| Chart invents facts | strengthen the specific template's RULES; add an eval case reproducing it; re-run eval |
| Chart format drifts from hospital style | user drops a de-identified sample in `samples/`; rebuild template from it (templates/README.md procedure) |
| Dictation mis-hears a term repeatedly | add line to `prompts/vocab-corrections.txt` |
| Generation slow (>60 s) | check Activity Monitor for memory pressure; close heavy apps; consider `gemma3:4b` |
| Ollama down after reboot | `brew services start ollama` |
