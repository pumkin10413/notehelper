# Chart Assistant (local, private)

Drafts English hospital charts from your bullet points or voice, entirely on this Mac.
Nothing is ever uploaded anywhere.

## Daily use (2 commands)
```bash
cd ~/Documents/Code/medicalchart
python3 app/server.py
```
Open **http://127.0.0.1:8765** → type bullets or hit 🎙 Dictate → pick chart type →
**Generate** → proofread → **Copy** → paste into the EMR.

Tip: make it one word — add to `~/.zshrc`:
`alias chartapp='cd ~/Documents/Code/medicalchart && python3 app/server.py'`

## Pasting a whole OPD record
Got several outpatient visits plus lab and exam reports instead of tidy bullets? Tick
**"Paste raw OPD record"** in the web app (or add `--raw` on the CLI). It cleans the text,
extracts a timeline, then writes the chart — two passes, ~1–3 min.
**Open "Extracted timeline" and check it first:** anything missing there cannot appear in the
chart, and scanning that list is much faster than proofreading prose against a 3-page record.
Pick chart type **`pi`** to get only the Present Illness paragraph, underlying diseases included.
Full guide + known limitations: [docs/OPD-RECORDS.md](docs/OPD-RECORDS.md).

## Browser-only option (no terminal, on-device Gemini Nano)
Double-click `app/chart-nano.html` (or serve it: `python3 -m http.server 8766 --directory app`
→ http://127.0.0.1:8766/chart-nano.html). Runs the bullets→chart step entirely in Chrome, no
server. Lower quality than the Ollama app above — proofread harder. Details: [docs/NANO.md](docs/NANO.md).

## Terminal one-liners
```bash
python3 scripts/chart.py --type admission --bullets "65M, DM/HTN, fever 3d, ..."
bash scripts/voice-chart.sh progress        # dictate, press Enter, get a SOAP note
bash scripts/doctor.sh                      # something broken? run this first
```

## Making it better over time
- Chart looks wrong / not your hospital's style → give a **de-identified** sample chart to a
  Claude session and say "add this as the admission template" (it knows the procedure).
- Dictation mis-hears a word → add `wrong => right` to `prompts/vocab-corrections.txt`.
- Anything else → open a Claude Code session in this folder; CLAUDE.md tells it everything.

**Every generated chart is a draft. You are the author — read every line before it enters
the medical record.**
