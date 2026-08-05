# Templates

Each `.md` file here is one chart type. The generation script (`scripts/chart.py`) reads the
template file whose name matches `--type` (e.g. `--type admission` → `admission.md`) and inserts
it into the LLM prompt.

## Template file format
A template has three parts, separated by `---` lines:

```
NAME: <human-readable name>
STYLE: <2-4 sentences describing tone/conventions for this chart type>
---
<THE SKELETON — the exact section headers and layout the output must follow>
---
RULES:
- <chart-type-specific rules the LLM must obey, one per line>
```

- The **skeleton** uses `[square brackets]` for slots the LLM fills from the user's bullets.
- A slot written as `[X / omit]` means: drop the whole line if the bullets contain nothing for it.
- Everything outside brackets (headers, fixed phrases, ordering) must be reproduced **verbatim**.

## Adding a template from a real chart (for any agent doing this)
1. Ask the user for a **de-identified** sample (checklist in [../docs/PHI-SAFETY.md](../docs/PHI-SAFETY.md)).
   Refuse to proceed if you see a name, chart number, national ID, exact birth date, or exact dates
   that could identify the patient — ask the user to replace them with placeholders first.
2. Save the raw de-identified sample in `samples/<type>-<nn>.md` (never overwrite; increment `nn`).
3. Derive/refresh the skeleton: keep the sample's exact section headers and ordering; replace
   patient-specific content with `[bracketed slots]`; move recurring fixed phrases (e.g.
   "The patient and family were informed...") into the skeleton verbatim.
4. If a template for that type already exists, back it up first: `cp admission.md admission.md.bak-$(date +%Y%m%d)`.
5. Add 1 new eval case in `eval/cases/` based on the sample (bullets in, expected-properties out).
6. Run the eval (see `eval/README.md`) before considering the change done.

## Current templates
- `admission.md` — Admission note (H&P). Priority 1.
- `procedure.md` — Procedure note. Priority 1.
- `consult.md` — Consultation reply. Priority 2.
- `progress.md` — Daily SOAP progress note. Priority 2.
- `pi.md` — **Present Illness only** (no headers/impression/plan). Built for raw OPD record input; favours completeness over brevity. See [../docs/OPD-RECORDS.md](../docs/OPD-RECORDS.md).

These skeletons are generic Taiwan-teaching-hospital style. They are meant to be **overwritten by
the user's real de-identified formats** — treat the user's samples as authoritative over these.
