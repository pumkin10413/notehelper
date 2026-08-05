# Pasting raw OPD records (multi-visit histories + exam reports)

For short bullets, the one-stage path is fine. For a **raw record dump** — several outpatient
visits, laboratory reports, and examination reports, pasted straight out of the hospital
system — use **raw mode**. It exists because a 7B model handed a long messy record *and* a
writing task at the same time silently drops facts.

## How to use it

**Web app** (`python3 app/server.py` → http://127.0.0.1:8765): tick **"Paste raw OPD record"**,
paste everything, pick the chart type, Generate. Takes ~1–3 min (two model passes). Then open
**"Extracted timeline"** under the output.

**CLI:**
```bash
pbpaste | python3 scripts/chart.py --type pi --raw --show-timeline
python3 scripts/chart.py --type admission --raw --file opd_dump.txt
```

## Read the timeline first — this is the workflow that matters
Raw mode runs **two passes**:

1. **Extract** (`prompts/system-extract.txt`) → a structured timeline: DEMOGRAPHICS,
   UNDERLYING, ALLERGY, MEDICATIONS, TIMELINE, LABS, STUDIES, NEGATIVES, DISPOSITION, UNCLEAR.
2. **Write** (`templates/<type>.md`) → the chart, composed **only** from that timeline.

Because stage 2 only sees the timeline, **anything missing from the timeline cannot appear in
the chart**. Checking the timeline (a compact, scannable list) is far faster and more reliable
than proofreading prose against a 3-page record. If a value is wrong there, fix it in the
timeline and regenerate, or correct the final text.

## Why two passes instead of one better prompt
| Failure with one pass | What fixes it |
|---|---|
| Context overflow — Ollama silently drops the OLDEST tokens, so the earliest visits vanish with no error | `pick_num_ctx()` in `scripts/chart.py` sizes the window (8k/16k/32k) from input length |
| Model must order, filter, dedupe, normalize units and write prose simultaneously → drops facts | Split into extraction, then composition |
| Boilerplate (banners, page numbers, order codes) eats context and distracts | `scripts/preprocess.py` strips it deterministically before any model runs |
| Underlying diseases buried in an old note get missed | UNDERLYING is its own mandatory extraction field, filled before any prose exists |

`scripts/preprocess.py` also converts full-width characters (Taiwan exports produce `４０mg`
→ `40mg`) and redacts patient name / chart number / national ID lines as defence-in-depth.

## Present Illness only
`--type pi` (`templates/pi.md`) outputs **only** the Present Illness narrative — no headers, no
chief complaint, no impression, no plan — ready to paste into the PI field. It is written to
**favour completeness over brevity**: every lab value and study finding in the input must appear,
and the opening sentence must carry all underlying diseases.

## Known limitations (verified 2026-07-08, qwen2.5:7b)
Real behaviour, not theory — check these when you review:
1. **Labs are sometimes lumped**, appearing after a lead-in like "Laboratory results included:"
   rather than woven into each visit's sentences. Happens roughly half the time. The values are
   correct and complete when it does; it is cosmetic. Edit the text or regenerate.
2. **Stage A occasionally drops one lab** from a multi-test collection date (HbA1c was the
   repeat offender). This is why you read the timeline.
3. A late visit's narrative can get compressed when the record is long.
4. `DEMOGRAPHICS` may guess a sex when the record states none. The `pi` template refuses to use
   it ("This patient"), but other templates may not — check it.

Hard rules the prompts now enforce (each was a real bug found and fixed on 2026-07-08):
- `r/o X` means X is **suspected**, never "X was ruled out".
- Never invent a disposition; a conditional plan ("admit if Hb low") is a plan, not a disposition.
- Never do arithmetic — "hypertension since 2018" stays "since 2018", never "(4 years)".
- Never invent age or sex; write "This patient".
- Never add an H/L flag the record did not print.

## Maintaining this
Change the extraction behaviour in `prompts/system-extract.txt`; change the prose behaviour in
`templates/<type>.md`. Fix at the layer where the defect is produced — see the layer table in
[eval/README.md](../eval/README.md) and the `/eval-prompts` skill. After ANY change run:
```bash
python3 eval/run_eval.py
```
`eval/cases/pi-raw-1.json` + `eval/fixtures/opd-dump-1.txt` cover this path; the fixture is
fully synthetic (no PHI) and deliberately nasty — out-of-order visits, full-width characters,
fake identifiers, and underlying diseases hidden in an old note.
