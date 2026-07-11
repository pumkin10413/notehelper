# PHI Safety Rules

This system exists because patient data must stay on this machine. These rules bind every
agent and every model that ever works in this repo. They are not negotiable.

## The three laws
1. **No chart content leaves the machine.** Bullets, transcripts, generated charts, and samples
   must never be sent to any cloud API, web search, telemetry, paste service, or git remote.
   The ONLY model that may see chart content is the local Ollama model at 127.0.0.1.
2. **Cloud models work on the system, not on patients.** Claude/Gemini/Hermes sessions may edit
   code, templates, prompts, and docs. If the user pastes real patient text into a cloud-model
   conversation, warn them once, then help — the user is responsible for their own pastes —
   but never store that text in the repo.
3. **Nothing identifying is written to disk in this repo.** `samples/` and `eval/cases/` accept
   de-identified text only (checklist below). Generated charts are not saved by the app at all.

## De-identification checklist (apply before saving ANY sample)
Remove or replace every one of these:
- [ ] Patient name → delete (use "the patient")
- [ ] Chart/medical record number → delete
- [ ] National ID / passport number → delete
- [ ] Exact dates → shift or genericize ("hospital day 3", "[date]"); year alone is OK
- [ ] Exact age >89 → "elderly"; otherwise age in years is OK
- [ ] Phone, address, occupation-with-employer, family members' names → delete
- [ ] Physician/staff names → role only ("the attending")
- [ ] Hospital/ward/bed identifiers → delete or genericize
- [ ] Rare-disease + demographic combos that identify a specific person → generalize

An agent asked to save a sample MUST scan for these items first. If any are present, do not
save — show the user what needs replacing and wait for a cleaned version.

## Technical containment (verify when touching these files)
- `app/server.py` binds `127.0.0.1` — never 0.0.0.0, never add remote access.
- `scripts/chart.py` talks only to `http://127.0.0.1:11434` — never point it at a hosted API.
- This repo has **no git remote** and must never get one while `samples/` exists.
  Check: `git -C <repo> remote -v` should print nothing.
- Model downloads (whisper/ollama) are inbound public files — allowed.

## External / cloud AI models (Gemini, ChatGPT, Copilot, Claude cloud, etc.)
"Local" means the model runs on THIS Mac: Ollama, whisper.cpp, or Chrome's on-device
Gemini Nano. Everything else is cloud — even if you open it in a browser tab on this machine.

- **Cloud models may NEVER see chart content** — no bullets, no transcripts, no generated
  charts, no real samples. Pasting patient data into gemini.google.com, the Gemini API, the
  "Gemini in Chrome" assistant, Gemini Advanced, ChatGPT, or Copilot is a PHI breach,
  identical to emailing it out.
- **Cloud models MAY build and maintain the system** — anything with no patient data in it:
  edit templates/prompts/scripts/docs, write new generic chart skeletons and eval cases,
  review architecture, refactor code, explain errors, suggest vetted local-model swaps.
- **Orchestration caveat:** if a cloud model (e.g. a Gemini/Chrome agent) is *driving* the
  pipeline, the patient bullets must not pass through its context. Route live patient data
  straight to the local model — the user runs `app/server.py` or `scripts/chart.py`
  themselves. A cloud agent that reads the bullets to "help format" them has already leaked them.
- **On-device Gemini Nano in Chrome — UNVERIFIABLE, treat as gray zone:**
  Chrome's built-in Prompt API (`window.ai` / Gemini Nano) claims to run inference on-device.
  Google says prompts stay local. However, **Chrome is closed-source telemetry software** —
  you cannot audit whether prompt text ever leaves the machine via usage metrics, crash
  reports, field trials, or future "quality improvement" telemetry. With Ollama/whisper.cpp
  you have an architectural guarantee (open source, 127.0.0.1 only, firewallable); with
  Chrome you have a policy promise from an ad company, revocable without notice.
  **Recommendation:** use `app/chart-nano.html` only for convenience with **non-sensitive or
  de-identified** content. For real patient data with identifiers, use the Ollama pipeline
  (`app/server.py` or `scripts/chart.py`) — that is the path you fully control.

## What the user must still do themselves
- Proofread every generated chart before it enters the medical record. The app shows this
  warning permanently; never remove it.
- Follow hospital policy on personal-device use. This tool drafts text; the EMR record and
  its accuracy remain the physician's responsibility.
