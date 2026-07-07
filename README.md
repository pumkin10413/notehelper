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
