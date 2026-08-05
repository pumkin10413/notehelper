---
name: chart
description: Generate a formatted medical chart (admission, procedure, consult, progress/SOAP note) from bullet points or a dictation transcript, using the local Ollama pipeline. Use whenever the user provides clinical bullets and wants a chart, note, or documentation drafted.
---

# Generate a chart

1. Identify the chart type from the request: `admission`, `procedure`, `consult`, `progress`
   (SOAP / daily note → progress), or `pi` (**Present Illness only** — use when the user asks
   for "just the present illness", "PI", or the history paragraph alone). If genuinely
   ambiguous, default to `progress` for ward updates and say which template you used.
2. Decide one-stage vs raw mode:
   - **Short bullets / dictation** → normal mode.
   - **A pasted record dump** (multiple OPD visits, dated notes, lab or exam reports, more than
     ~40 lines, hospital boilerplate) → add `--raw`. This cleans the text, extracts a timeline,
     then writes. Takes ~1-3 min. Details: docs/OPD-RECORDS.md.
3. Run the local pipeline (do NOT draft the chart yourself unless the local model is broken):
   ```bash
   python3 scripts/chart.py --type <type> --file <tempfile with the input>
   python3 scripts/chart.py --type <type> --raw --show-timeline --file <tempfile>   # raw mode
   ```
   Write the user's text to a temp file first (quotes/newlines break --bullets).
   In raw mode, show the user the extracted timeline as well as the chart, and tell them:
   "anything missing from the timeline cannot appear in the chart — check it first."
4. Show the full output to the user, then append this line:
   "Draft only — please verify every value and statement before it goes into the record."
5. If the script errors: `bash scripts/doctor.sh` and apply the fix it names, then retry once.
6. If the output invented a fact or broke format: fix per the table in docs/ARCHITECTURE.md
   ("Failure modes"), which routes you to template RULES + a new eval case — never leave it
   unrecorded, that's how the system learns.

Never send the clinical content to any web/cloud tool. Local model only (PHI-SAFETY.md).
