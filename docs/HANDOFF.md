# Handoff Log & Session Plan

Newest session entry goes at the TOP of the log. Every working session in this repo — whatever
model runs it — ends by appending an entry here (format at the bottom).

## How to run a session on a Claude Pro quota (read first)
- One session = ONE goal from the roadmap below. Do not start a second goal in the same session.
- First 3 actions of any session: read CLAUDE.md → read the latest handoff entry → run
  `bash scripts/doctor.sh`. Then work.
- Write results to files as you go. When ~80% of the session budget feels used, stop working
  and write the handoff entry; an unfinished-but-recorded task beats a finished-but-lost one.
- Commit at the end: `git add -A && git commit -m "<what changed>"`. Never add a git remote.

## Roadmap (do in order; one line = one session; ✅ = done)
1. ✅ Bootstrap: install stack, templates/prompts/scripts/app/eval/docs, smoke tests. (2026-07-07, Fable 5)
2. ☐ **Realism pass:** user brings 1-2 de-identified REAL charts per priority type
   (admission, procedure). Use `/add-template` skill to rebuild those templates from them,
   add eval cases, run full eval. This is the single highest-value remaining task.
3. ☐ **Daily-driver tuning:** user has used the web app for real work ≥3 days. Collect
   every complaint (wrong phrasing, slow, mis-transcriptions). Fix each via the
   `/eval-prompts` fix loop + `vocab-corrections.txt`. Add a `consult`/`progress` real sample
   if available.
4. ☐ **Voice ergonomics:** if CLI dictation is used, tune it (mic levels, medium.en model if
   accuracy complaints — SETUP.md upgrade table). If the user rarely dictates, skip and pull
   the next roadmap item forward.
5. ☐ **New chart types** the user actually needs (discharge summary is the likely first —
   create `templates/discharge.md` via `/add-template` from a real sample + eval case).
6. ☐ **Personal phrase library:** recurring attending-specific or service-specific phrasings
   the user keeps retyping → move into template fixed text or a new `prompts/phrases-<service>.txt`
   wired into the template. Only do this after several weeks of real usage data.
7. ☐ Periodic: re-run full eval after any `brew upgrade` of ollama/whisper-cpp; check
   docs/ARCHITECTURE.md "vetted alternatives" if a clearly better ≤8B model has appeared.

Rules for the roadmap: if the user's request in a session differs from the next ☐ item, do the
user's request (they outrank the roadmap), then update the roadmap to reflect reality.

## Handoff entry format (append-at-top, copy this)
```
## YYYY-MM-DD — <model name> — <one-line goal>
Done: <what was completed, file paths>
Not done / broken: <anything left dangling, with the exact error if any>
Eval: <pass/fail count, or "not run" + why>
Next session should: <one concrete goal>
```

---

## 2026-07-08 — Claude (Opus 4.8) — Add on-device Gemini Nano browser fallback
Done:
- Documented the cloud-vs-local boundary for external models in docs/PHI-SAFETY.md
  ("External / cloud AI models" section) — Gemini/ChatGPT/etc. may build the system but never
  see patient data; only on-device Nano is PHI-safe for chart content.
- Built `app/chart-nano.html`: single self-contained file, bullets+labs → chart entirely on
  Chrome's on-device Gemini Nano (Prompt API), no server/network/CDN. Templates embedded
  (snapshot of templates/*.md) + a user "custom…" template slot (localStorage). Defensive
  across Chrome API versions; fresh session per chart (no cross-patient context); NO browser
  speech input (that would be cloud/PHI). Docs in docs/NANO.md; router + README updated;
  `nano-static` added to .claude/launch.json for http serving.
Not done / broken:
- End-to-end Nano inference not run (needs one-time ~2 GB model download on the user's Chrome).
  Everything up to the model call is verified (load, graceful degradation, API-drift handling,
  exact prompt assembly, custom-template guard).
- This is a FALLBACK. Default remains app/server.py + Ollama qwen2.5:7b (higher quality).
Eval: run_eval.py unchanged and not re-run (no change to prompts/ or templates/ source; the
Nano file has its own embedded snapshot). Still 4/4 from 2026-07-07.
Next session should: Roadmap item 2 — rebuild admission + procedure templates from the user's
real de-identified samples (`/add-template`). When you do, also re-copy them into the embedded
snapshot in app/chart-nano.html (see docs/NANO.md "Maintaining it").

## 2026-07-07 — Claude Fable 5 — Bootstrap the entire system
Done:
- Installed ollama + whisper-cpp + ffmpeg (Homebrew); whisper model `models/ggml-small.en.bin`;
  Ollama runs as a login service (`brew services start ollama`).
- Built: templates/ (admission, procedure, consult, progress), prompts/system-chart.txt +
  vocab-corrections.txt, scripts/ (chart.py, dictate.sh, voice-chart.sh, doctor.sh, vocab_fix.py),
  app/server.py + index.html (127.0.0.1:8765), eval/ (runner + 4 cases), docs/ (SETUP,
  ARCHITECTURE, PHI-SAFETY, this file), AGENTS.md, CLAUDE.md, 3 skills in .claude/skills/.
- Verified: doctor.sh all-pass (see below), whisper transcription tested with synthetic audio
  (correct, even normalized "128 over 76"→"128/76"), git repo initialized (no remote, by design).
Not done / broken:
- `.claude/settings.json` (permission allowlist) could not be written by the agent (harness
  blocks self-modification). User should apply docs/proposed-permissions.md manually.
- Templates are generic skeletons — not yet matched to the user's real hospital formats
  (that is roadmap item 2, deliberately).
- CLI mic dictation (`scripts/dictate.sh` live recording) untested — needs the user present
  to grant the one-time macOS microphone permission. File-based transcription verified working.
Eval: 4/4 pass (admission, procedure, consult, progress). One eval-harness fix during the
session: A2 number check now ignores list-item numerals ("4." at line start) — that was a
checker false positive, not a model hallucination.
Next session should: Roadmap item 2 — rebuild admission + procedure templates from the user's
real de-identified samples using the `/add-template` skill.
