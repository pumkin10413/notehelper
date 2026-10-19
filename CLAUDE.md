# medicalchart — Local Medical Charting Assistant

Local-only charting assistant for a resident in a Taiwan hospital (charts written in English).
Voice → text via whisper.cpp; bullets → formatted chart via Ollama. **No patient data ever leaves this machine.**

## Hard rules (never violate)
1. **PHI stays local.** Never send chart content, transcripts, or samples to any cloud API, web search, or external service. See [docs/PHI-SAFETY.md](docs/PHI-SAFETY.md).
2. **Backup before modifying.** Copy any existing file to `<name>.bak-YYYYMMDD` (or rely on a git commit) before editing it.
3. **Write as you go.** Save completed work to files immediately; never hold results only in conversation.
4. **This file stays short.** It is a router. Put new content in `docs/` and link it here.

## Where things are
| What | Where |
|---|---|
| System design & model choices | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Install & verify everything | [docs/SETUP.md](docs/SETUP.md) |
| PHI / de-identification rules | [docs/PHI-SAFETY.md](docs/PHI-SAFETY.md) |
| Pasting raw OPD records (multi-visit + exam reports) | [docs/OPD-RECORDS.md](docs/OPD-RECORDS.md) |
| Session plan + handoff log | [docs/HANDOFF.md](docs/HANDOFF.md) |
| Chart templates | [templates/](templates/README.md) |
| LLM prompts (bullets→chart) | [prompts/](prompts/README.md) |
| CLI tools | [scripts/](docs/ARCHITECTURE.md) — `chart.py`, `dictate.sh`, `voice-chart.sh`, `doctor.sh` |
| **ACTUAL TOOL IN USE (from 2026-08)** — Google Sheets + bound Apps Script | [docs/SHEETS-BACKEND.md](docs/SHEETS-BACKEND.md) |
| Superseded browser page, bullets → Present Illness | `app/chart-nano.html`, published copy `index.html` — see [docs/NANO.md](docs/NANO.md) |
| Ollama web app (**not being developed** — user paused this path 2026-08-06) | `app/server.py` → http://127.0.0.1:8765 |
| Regression tests for prompts | [eval/](eval/README.md) |
| De-identified real samples | `samples/` (user adds; follow PHI-SAFETY checklist) |
| Instructions for non-Claude agents | [AGENTS.md](AGENTS.md) |

## Current direction (read before planning work)
**The user now works in a Google Sheet ("chart") with a container-bound Apps Script —
see [docs/SHEETS-BACKEND.md](docs/SHEETS-BACKEND.md). Both the browser page and the Ollama
pipeline are superseded.** The bound script's source is NOT reachable through the Drive
connector; open it via the sheet → Extensions → Apps Script.

Older note (kept for context): the user previously worked in the **browser page**
(`app/chart-nano.html` / hosted `index.html`), not the Ollama stack. That page was deliberately simplified on 2026-08-07 to do ONE job: bullets →
Present Illness. **Do not add features to it unless asked** — raw-OPD parsing, other chart
types and the timeline panel were all removed on purpose (they still exist in the Ollama
pipeline, and an unfinished no-AI engine is parked on branch `wip/builtin-engine`).
**After editing `app/chart-nano.html`, run `cp app/chart-nano.html index.html`** or the hosted
page goes stale.

## Common tasks
- **Health check first**: `bash scripts/doctor.sh` — run this before debugging anything.
- **Generate a chart**: `python3 scripts/chart.py --type admission --bullets "..."` or use the `/chart` skill.
- **Raw OPD record** (multiple visits + lab/exam reports): add `--raw` — `python3 scripts/chart.py --type pi --raw --show-timeline --file dump.txt`. Two passes; read the timeline first. See [docs/OPD-RECORDS.md](docs/OPD-RECORDS.md).
- **Present Illness only**: `--type pi` — outputs just the PI narrative, underlying diseases included.
- **Start the web app**: `python3 app/server.py` then open http://127.0.0.1:8765
- **Add a template from a sample**: use the `/add-template` skill; de-identify first (PHI-SAFETY.md checklist).
- **Changed a prompt or template?** Run the eval: see [eval/README.md](eval/README.md). Do not ship a prompt change that fails eval.

## Environment facts
- MacBook Air M3, 16 GB RAM, macOS 14. Local LLM runs via Ollama (`qwen2.5:7b-instruct`), STT via whisper.cpp (`small.en`), audio via ffmpeg. All installed with Homebrew.
- Python is system 3.9 — all project Python must be stdlib-only and 3.9-compatible (no `match`, no `X | Y` type syntax).
- Ollama API: `http://127.0.0.1:11434`. Start with `ollama serve` if doctor.sh says it's down.
