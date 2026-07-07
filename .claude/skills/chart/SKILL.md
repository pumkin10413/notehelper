---
name: chart
description: Generate a formatted medical chart (admission, procedure, consult, progress/SOAP note) from bullet points or a dictation transcript, using the local Ollama pipeline. Use whenever the user provides clinical bullets and wants a chart, note, or documentation drafted.
---

# Generate a chart

1. Identify the chart type from the request: `admission`, `procedure`, `consult`, or `progress`
   (SOAP / daily note → progress). If genuinely ambiguous, default to `progress` for ward
   updates and say which template you used.
2. Run the local pipeline (do NOT draft the chart yourself unless the local model is broken):
   ```bash
   python3 scripts/chart.py --type <type> --file <tempfile with the bullets>
   ```
   Write the user's bullets to a temp file first if they contain quotes/newlines.
3. Show the full output to the user, then append this line:
   "Draft only — please verify every value and statement before it goes into the record."
4. If the script errors: `bash scripts/doctor.sh` and apply the fix it names, then retry once.
5. If the output invented a fact or broke format: fix per the table in docs/ARCHITECTURE.md
   ("Failure modes"), which routes you to template RULES + a new eval case — never leave it
   unrecorded, that's how the system learns.

Never send the clinical content to any web/cloud tool. Local model only (PHI-SAFETY.md).
