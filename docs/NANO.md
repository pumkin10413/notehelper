# The on-device page (`app/chart-nano.html` — the primary tool)

A single self-contained HTML file that turns bullets, dictated text, or a **whole pasted OPD
record** into a formatted English chart using Chrome's built-in on-device Gemini Nano
(Prompt API). No server, no terminal, no network calls, no external scripts.

`index.html` at the repo root is a **byte-identical copy** published via GitHub Pages at
https://pumkin10413.github.io/notehelper/ . **After editing `app/chart-nano.html` you must
re-copy it**, or the hosted page silently goes stale:
```bash
cp app/chart-nano.html index.html
```

## What it does
- Chart types: **`pi`** (Present Illness only), `admission`, `procedure`, `consult`,
  `progress`, plus a **custom…** slot saved in the browser (localStorage).
- **Paste raw OPD record** checkbox: cleans the text, extracts a structured timeline in as many
  chunks as the browser's context allows, merges them deterministically, then writes the chart.
- **Extracted timeline** panel: the chart is written *only* from this, so anything missing here
  is missing from the chart. You can **edit the timeline and press "Rewrite chart"** — the
  fastest way to fix a bad output without re-running extraction.
- **Model & setup check**: reports the Prompt API flavour, availability, context window, and
  whether the browser is an echo stub. Run this first when anything looks wrong.

## Hard-won constraints (measured 2026-08-06 — do not undo these)
1. **Never hardcode a context size.** Nano's window differs between Chrome builds. Budgets come
   from `session.contextWindow` + `measureContextUsage()` at runtime (`charBudget()`), reserving
   45% of the window for the answer. If the browser reports nothing, a conservative fallback is
   used. This is why long records are chunked into "as many pieces as *this* browser needs".
2. **Echo-stub detection is a safety feature, not a nicety.** Some Chromium builds expose the
   Prompt API with no model and echo the prompt back verbatim. Without `detectStub()` the page
   would display the physician's own input as a finished chart. It now raises a hard error and
   leaves the output empty. Never remove this guard.
3. **The model download needs a real user gesture.** Chrome throws
   `NotAllowedError: Requires a user gesture` if `create()` is called outside a click handler,
   so creation must stay inside the Generate/check button handlers.
4. **No speech input here.** Chrome's `webkitSpeechRecognition` sends audio to Google, which
   would be a PHI breach. Voice stays in the local whisper pipeline (`scripts/dictate.sh`).
5. **Session creation is the slow part — do not add sessions.** `LanguageModel.create()` is by
   far the most expensive call; prompting an existing session is cheap. So:
   - one generation creates **two** sessions total (one for the whole extraction phase, one for
     the write), never one per chunk. `runMany()` owns the extraction session;
   - each chunk runs on `session.clone()`, which resets the conversation to the system prompt so
     calls stay independent *without* paying for a create and *without* accumulating context
     across chunks. `promptOn()` falls back to reusing the session if `clone` is missing;
   - `charBudget()` measures on the session that already exists and **caches** the result for the
     page's lifetime — it depends on the browser, not on the record. Re-measuring per Generate
     wasted a whole session creation.
   Earlier versions created a session per chunk plus a throwaway one for the budget (N+2 per
   run); that is what made it feel slow. Keep it at 2.
6. **Prompts are deliberately short.** Every character of system prompt and template is one the
   record cannot use. Keep the safety rules, cut the prose. Do not paste the long
   `templates/*.md` bodies in here — the embedded ones are intentionally condensed.

## Measured on the user's real Chrome (2026-08-06)
```
Prompt API:      LanguageModel
Availability:    available
Context window:  9216 tokens
Echo stub:       no
Sample reply:    ok
```
Real Gemini Nano works on this machine and reports a **9216-token** window — 9× the 1000 the
Chromium echo stub reported. Consequences:
- Most single OPD records fit in **one chunk**, so cross-chunk merge artifacts are rare. Chunking
  still matters for long records and must stay.
- There is room for reasonably detailed templates; they no longer need to be squeezed to the
  bone. Do not bloat them without cause, but do not sacrifice a safety rule to save 200 chars.
- `charBudget()` reserves 45% of the window for the answer, so ~4,700 tokens of record per
  extraction call. Tune that reserve only with a measurement, not a guess.

## Verified vs unverified (be honest with the user about this)
Verified in a Chromium test browser on 2026-08-06:
- deterministic cleaning: identifiers (name / chart no / Taiwan national ID) removed, full-width
  `４０mg`→`40mg`, page/print/separator boilerplate dropped;
- chunking adapts to the budget (2 chunks at a 300-char budget, 1 at 5000);
- timeline merge across chunks: dedupes, prefers real values over "not stated", takes the last
  real DISPOSITION, and re-sorts events chronologically even when chunks arrive out of order;
- echo-stub detection: catches the stub, does not false-positive on real prose;
- the failure path: clear error, empty chart, diagnostics auto-opened.

**NOT verified: real Gemini Nano generation quality.** The available test browser was Chromium
with an echo stub, so no real chart has ever been produced by this page. The first person to run
it on a proper Chrome must judge whether Nano's output is good enough, and how much of a record
fits per chunk. Expect Nano to be markedly weaker than a 7B model at following the template.

## BLOCKER: Gemini Nano does not run on the hospital VDI (confirmed 2026-08-06)
The user charts inside a **Windows virtual desktop reached through Omnissa Horizon Client** —
that is where the EMR lives. On that VDI Chrome the page reports **"no on-device model /
unavailable"**. Their MacBook's Chrome reports available with a 9216-token window; the two are
different browsers on different machines, and only the Mac one works.

**Why is UNRESOLVED — do not repeat the earlier overclaim.** An earlier version of this file
asserted that managed policy, missing GPU passthrough and profile wiping made it "almost
certainly not fixable". That was inference from a single "unavailable" reading, not evidence.
Since then the VDI Chrome was found to be **version 151.0.7922.76**, far above the 138 minimum,
so the version hypothesis is dead and the rest are still untested.

Chrome refuses the model when ANY of these fails, and all produce the same "unavailable":
| Requirement | Fixable by the user? |
|---|---|
| Chrome 138+ | **Ruled out** — VDI runs 151 |
| Both flags on (they are OFF by default) | **Yes**, if policy allows — most likely cause |
| > 4 GB VRAM | No — the real risk on a GPU-less virtual desktop, though "Enabled BypassPerfRequirement" is designed to relax exactly this |
| ~22 GB free on the profile volume | No |
| Enterprise policy permitting the local model | No — check `chrome://policy` |

**Diagnose, do not guess:** `chrome://on-device-internals` on the machine in question names the
failing criterion; `chrome://policy` shows whether IT disabled the local foundational model.
Record the answer here when it is known.

Regardless of the outcome, the page must not *depend* on Nano: the user's stated requirement is
that it "work on almost any machine with new Chrome, even hospital Windows computers". That is
what the built-in no-AI engine is for.

## If the page says the model is unavailable
Only do this when "Run check" reports unavailable. On this user's machine it already reports
available, so setup is done.

**Do not hand anyone a `chrome://flags/#flag-name` deep link.** Two reasons it appears broken:
Chrome refuses to let a web page navigate to a `chrome://` URL at all (it must be pasted into the
address bar), and the `#anchor` only highlights a flag when that exact ID exists in that build —
if the flag was renamed or now ships enabled by default, you land on a plain flags page with
nothing selected. Tell people to use the flags **search box** instead.

1. `chrome://version` — need **Chrome 138+**, and real Chrome. Chromium usually has no model and
   silently echoes the prompt back (see the stub guard above).
2. `chrome://flags` → search `on-device`, then `prompt api`:
   - "Prompt API for Gemini Nano" → **Enabled**
   - "Enables optimization guide on device" → **Enabled BypassPerfRequirement** (not plain Enabled)
   - A search returning nothing usually means that piece already ships enabled — move on.
3. Relaunch, then `chrome://on-device-internals` for the one-time ~2 GB download. This page, not
   the flags page, is the authority on whether the model is actually present.
4. Press **Run check** on the page.

## Maintaining it
All logic is exposed as `window.NanoCore` so it can be tested from the console without the UI:
```js
NanoCore.cleanRecord(text)        // {cleaned, stats}
NanoCore.chunkRecord(text, 1200)  // string[]
NanoCore.mergeTimelines([...])    // merged timeline object
NanoCore.probeCapabilities()      // what this browser can actually do
```
Change extraction behaviour in `SYS_EXTRACT`, prose behaviour in `TEMPLATES[...]`, both near the
top of the `<script>`. The embedded templates are condensed relatives of `templates/*.md`; when
you change one, consider whether the other needs the same fix, and re-copy to `index.html`.
