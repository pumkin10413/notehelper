# The Google Sheets backend (the tool actually in use, from 2026-08)

**This, not `app/chart-nano.html`, is what the user uses.** The browser page and the Ollama
pipeline in this repo are both superseded. Discovered 2026-10-19.

## What it is
A Google Sheet titled **"chart"** (an ENT ward / OR list), with a **container-bound Apps
Script** that fills in the Present Illness for each row.

Sheet columns (Sheet1):
| Col | Header | Role |
|---|---|---|
| A | 病歷號碼 | chart number — identifier |
| B | 姓名 | name — identifier |
| D / E | 性別 / 年齡 | sex / age |
| G | **診斷** | the diagnosis — structured, use as `[Diagnosis]` |
| H | **術式** | the operation — structured, use as `[operation]` |
| L | **病史** | INPUT: the raw EMR dump (Diagnosis / Subjective / Objective / Assessment & Plan) |
| M | chart template | present but empty — intended per-row template override |
| N | **現病史** | OUTPUT: the generated Present Illness |
| O | 狀態 | run status, e.g. `done - checks clean - 10:42 #a414751f` |

A second sheet, 術前準備, holds pre-op checklists — unrelated to the PI generation.

## Where the code lives — and the catch
The script is **bound to the spreadsheet**, so it does NOT appear in Drive file search and its
source cannot be read through the Drive connector. The standalone scripts in Drive are
unrelated ("ENT practice" is a Telegram-driven document-filing system; it never calls
`SpreadsheetApp`).

To edit it: open the sheet → **Extensions → Apps Script**. That is the only route found so far.

## Design note that matters
Because 診斷 (G) and 術式 (H) are **their own columns**, the scheduled-surgery sentence should be
filled from those cells directly rather than inferred from the prose in 病史. That is both more
reliable and cheaper than asking the model to find them. And since this sheet is an operating
list, the scheduled-operation ending is the normal case, not the exception.

## Requested rules (2026-10-19) — paste into the Present Illness prompt
```
PAST HISTORY AND SOCIAL HISTORY ALWAYS COME FIRST, before anything about the current illness:
1. Past history in the first sentence: "This [age]-year-old [man/woman] with underlying [EVERY
   chronic disease and previous operation in 病史, most relevant first, keeping each year exactly
   as written, previous operations as "s/p [operation] in [year]"]". If none are given, write
   "no known systemic disease". Never guess an age or sex that is not stated — write "This
   patient" and omit the sex.
2. Social history immediately after, in its own sentence: smoking (amount and duration),
   alcohol, betel nut — using ONLY what 病史 states. If 病史 says nothing about them, write
   nothing about them. Never write "denies smoking" unless it actually says so.
3. Only then the current illness.

CLOSING — if the patient is being admitted for a scheduled/elective operation, end with exactly
this wording, taking [Diagnosis] from column G (診斷) and [operation] from column H (術式) and
writing the operation identically in both places:

"[Diagnosis] was impressed. After informing the indications and risks of [operation], the
patient decided to receive the operation. Hence, the patient was admitted for scheduled
[operation]."

Do not reword, shorten or embellish those three sentences. If there is no scheduled operation
and no other stated disposition, write no closing sentence at all — never invent one.
```

## PHI
This backend puts identifiable patient data (names, chart numbers, full histories) in Google
Sheets, and any connector that reads the sheet carries that data to wherever the assistant runs.
That is a deliberate departure from this repo's original "PHI never leaves the machine" rule
(docs/PHI-SAFETY.md), which assumed a local-only pipeline. Do not quote patient rows into a
conversation or into any file in this repo; work on the prompt, not on the data.
