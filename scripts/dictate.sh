#!/bin/bash
# Record from the microphone, transcribe locally with whisper.cpp, print the text.
#
# Usage:
#   bash scripts/dictate.sh              # record until you press Enter, then transcribe
#   bash scripts/dictate.sh 30           # record exactly 30 seconds
#   bash scripts/dictate.sh --wav f.wav  # transcribe an existing audio file instead
#
# Requires: ffmpeg, whisper-cli (brew install ffmpeg whisper-cpp), and the model file
# models/ggml-small.en.bin. First run: macOS will ask to grant the Terminal microphone
# access (System Settings > Privacy & Security > Microphone).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODEL="$ROOT/models/ggml-small.en.bin"
TMPWAV="$(mktemp -t dictate).wav"
trap 'rm -f "$TMPWAV"' EXIT

[ -f "$MODEL" ] || { echo "ERROR: missing $MODEL — see docs/SETUP.md (whisper model download)." >&2; exit 1; }

if [ "${1:-}" = "--wav" ]; then
  # Transcribe an existing file (any format ffmpeg can read).
  ffmpeg -loglevel error -y -i "$2" -ar 16000 -ac 1 -c:a pcm_s16le "$TMPWAV"
elif [ -n "${1:-}" ]; then
  echo "Recording for $1 seconds..." >&2
  ffmpeg -loglevel error -y -f avfoundation -i ":0" -t "$1" -ar 16000 -ac 1 -c:a pcm_s16le "$TMPWAV"
else
  echo "Recording... press Enter to stop." >&2
  ffmpeg -loglevel error -y -f avfoundation -i ":0" -ar 16000 -ac 1 -c:a pcm_s16le "$TMPWAV" &
  FFPID=$!
  read -r
  kill -INT "$FFPID" 2>/dev/null || true
  wait "$FFPID" 2>/dev/null || true
fi

TEXT="$(whisper-cli -m "$MODEL" -f "$TMPWAV" --no-timestamps 2>/dev/null | sed 's/^ *//')"

# Apply medical vocabulary corrections (prompts/vocab-corrections.txt).
printf '%s\n' "$TEXT" | python3 "$ROOT/scripts/vocab_fix.py"
