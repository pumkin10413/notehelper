# Browser-only fallback: app/chart-nano.html (on-device Gemini Nano)

A single self-contained HTML file that does the bullets+labs → paragraph chart step **entirely
in Chrome** using the built-in on-device Gemini Nano (Prompt API). No server, no terminal, no
network calls, no external scripts. This is the experimental fallback from
[ARCHITECTURE.md](ARCHITECTURE.md); the **default, higher-quality path is still
`app/server.py` + Ollama qwen2.5:7b** (see [../README.md](../README.md)).

## Why it exists / when to use it
- Zero-terminal, browser-only charting; or a laptop where Ollama isn't running.
- Google says Gemini Nano runs on-device, but Chrome is closed-source — you cannot verify
  that prompts never leave the machine via telemetry, crash reports, or field trials. **Use
  for de-identified or non-sensitive content only.** For real patient data with identifiers,
  use the Ollama pipeline instead. See [PHI-SAFETY.md](PHI-SAFETY.md) → "On-device Gemini
  Nano in Chrome" for the full reasoning.
- **Quality is lower than the default pipeline** — Nano is a small model with a small context
  window. Proofread harder. Prefer the Ollama app when it's available.

## How to open it
Either:
- Double-click `app/chart-nano.html` (file:// is a secure context in Chrome), or
- Serve it locally and open http://127.0.0.1:8766/chart-nano.html:
  `python3 -m http.server 8766 --directory app`
  (http origin is sometimes needed for the Prompt API; the `nano-static` entry in
  `.claude/launch.json` starts exactly this.)

First "Generate" downloads the Nano model (~2 GB, one time); the status line shows progress.
If the page says Nano isn't available, follow the on-page "Enable it" steps (Chrome 138+,
two `chrome://flags`, then `chrome://on-device-internals`).

## What it deliberately does NOT do
- **No voice input.** Chrome's `webkitSpeechRecognition` sends audio to Google (cloud) = PHI
  breach. Voice stays in the local whisper pipeline (`scripts/dictate.sh`). Do not add browser
  speech recognition to this file.
- No persistence of charts. A fresh model session is created per generation (no cross-patient
  context) and destroyed after.

## Maintaining it (for any model editing this file)
- The 4 templates and the system prompt are **embedded snapshots** of `templates/*.md` and
  `prompts/system-chart.txt` (search `TEMPLATE SNAPSHOT` and `const SYS` in the HTML). If you
  change those source files, re-copy the relevant text into the HTML, or the two paths drift.
  The embedded system prompt is intentionally a *trimmed* version — Nano's context is small;
  keep it short but never weaken the "NEVER invent facts" rules.
- The Prompt API changes between Chrome versions. The code already handles: global
  `LanguageModel` vs `window.ai.languageModel` vs legacy `createTextSession`; missing
  `LanguageModel.params()`; `initialPrompts` vs `systemPrompt`; cumulative vs delta streaming.
  If a new Chrome breaks it, extend `createSession()` / `availability()` defensively (try/catch
  a new shape, fall back to the old) rather than replacing what's there.
- Users can add their own template in the UI ("custom…" option, saved to localStorage) without
  editing the file. That is the supported way for the user to try a format; promoting it to a
  real template still goes through the `/add-template` skill + eval.

## Verified 2026-07-08
Page loads with no JS errors; degrades gracefully when Nano is absent; on a Chrome with the
Prompt API it reported `availability: downloadable` and enabled Generate; prompt assembly
matches `chart.py` exactly (`TEMPLATE:\n…\n\nPHYSICIAN INPUT:\n…`); custom-empty guard works.
End-to-end inference not run here (needs the one-time model download on the user's machine).
