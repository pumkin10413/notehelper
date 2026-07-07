# Setup & Verification

Everything below was installed and verified on 2026-07-06 on the MacBook Air M3 / 16 GB.
This file exists so any model (or the user on a new machine) can rebuild the stack from zero.

## One-command health check
```bash
bash scripts/doctor.sh
```
If everything PASSes, skip the rest of this file.

## Full install from scratch

### 1. Homebrew packages
```bash
brew install ollama whisper-cpp ffmpeg
```
Verify: `command -v ollama whisper-cli ffmpeg` prints three paths.

### 2. Ollama service + chart model (~4.7 GB download)
```bash
brew services start ollama          # starts now AND on every login
ollama pull qwen2.5:7b-instruct
```
Verify: `curl -s http://127.0.0.1:11434/api/version` returns a version JSON, and
`ollama list` shows `qwen2.5:7b-instruct`.

### 3. Whisper speech model (~466 MB download)
```bash
curl -sL -o models/ggml-small.en.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin
```
Verify: `ls -lh models/ggml-small.en.bin` shows ~466M.
(This is a public model file, not patient data — downloading it is fine.)

### 4. Microphone permission (one-time, user must do it)
- **CLI dictation**: the first `bash scripts/dictate.sh` makes macOS prompt for
  microphone access for your terminal app. If it silently records nothing:
  System Settings → Privacy & Security → Microphone → enable your terminal.
- **Web app dictation**: the browser shows its own mic prompt on first use of 🎙 Dictate.

### 5. Smoke test (end to end, no patient data)
```bash
python3 scripts/chart.py --type progress \
  --bullets "patient stable, no fever overnight, BP 128/76, lungs clear, keep current antibiotics, check CBC tomorrow"
```
Expected: a SOAP note with S/O/A/P sections, BP 128/76 in O, no invented values.
Then: `python3 app/server.py` → open http://127.0.0.1:8765 → generate the same note in the UI.

## Upgrades (only when the user asks / quality is insufficient)
| Want | Do | Cost |
|---|---|---|
| Better dictation accuracy | download `ggml-medium.en.bin` (~1.5 GB) the same way as step 3; change `MODEL=` in `scripts/dictate.sh` and `WHISPER_MODEL` in `app/server.py` | slower transcription |
| Different chart model | `ollama pull <model>`; set env `CHART_MODEL=<model>` or edit `DEFAULT_MODEL` in `scripts/chart.py` | see docs/ARCHITECTURE.md for vetted choices |

## Known constraints
- System Python is 3.9 → project code is stdlib-only, 3.9-syntax only.
- 16 GB shared RAM: do not run two LLMs at once; qwen2.5:7b (Q4, ~4.7 GB) + whisper-small
  coexist fine. Models ≥ 12B are NOT recommended on this machine.
- ~65 GB free disk at setup time. Current models use ~5.2 GB total.
