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

## What the user must still do themselves
- Proofread every generated chart before it enters the medical record. The app shows this
  warning permanently; never remove it.
- Follow hospital policy on personal-device use. This tool drafts text; the EMR record and
  its accuracy remain the physician's responsibility.
