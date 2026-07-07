# Prompts

Prompt files consumed by `scripts/chart.py` and `app/server.py`. Plain text so any agent or
runtime (Claude, Hermes, Gemini, raw Ollama) can use them unchanged.

| File | Used for |
|---|---|
| `system-chart.txt` | System prompt for bullets/transcript → chart. The user message is built by `chart.py` as: `TEMPLATE:\n<template file>\n\nPHYSICIAN INPUT:\n<bullets>` |
| `vocab-corrections.txt` | Post-STT find→replace list for medical terms whisper gets wrong. Format: `wrong term => correct term`, one per line, `#` comments allowed. Applied case-insensitively by `scripts/dictate.sh` and the web app before the text reaches the user/LLM. |

## Rules for editing prompts (any model doing this, read carefully)
1. **Back up first**: `cp system-chart.txt system-chart.txt.bak-$(date +%Y%m%d)`.
2. **Run the eval after every change**: see [../eval/README.md](../eval/README.md). A prompt edit
   that fails any MUST-PASS check gets reverted, not patched around.
3. The target model is a **7B local model** (qwen2.5:7b-instruct). Keep instructions:
   - imperative and concrete ("Output ONLY the chart text"), never abstract ("be professional");
   - front-loaded — the most important constraints (no invented facts) stay in their own
     ALL-CAPS-headed block;
   - short — if the prompt exceeds ~600 words, cut before adding.
4. The no-hallucination block (`ABSOLUTE PROHIBITIONS`) is the safety core of this system.
   Never weaken it to fix a formatting complaint; fix formatting in the template instead.
5. Prefer fixing behavior in **templates** (per-chart-type RULES) over the system prompt.
   The system prompt is global; template RULES are local and safer to change.

## Growing `vocab-corrections.txt`
When the user reports a mis-transcribed term, append a line. Keep it sorted alphabetically.
Only add unambiguous corrections (a term that is *always* wrong→right in this user's practice).
Never add a correction that changes one valid drug name into another based on guesswork.
