#!/bin/bash
# Health check for the whole charting stack. Run this FIRST whenever anything misbehaves.
# Prints PASS/FAIL per component with the exact fix command for each failure.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0

check() {  # check <label> <fix-hint> <command...>
  local label="$1" fix="$2"; shift 2
  if "$@" >/dev/null 2>&1; then
    echo "PASS  $label"
  else
    echo "FAIL  $label"
    echo "      fix: $fix"
    FAIL=1
  fi
}

check "ffmpeg installed"        "brew install ffmpeg"        command -v ffmpeg
check "whisper-cli installed"   "brew install whisper-cpp"   command -v whisper-cli
check "whisper model present"   "see docs/SETUP.md step 3"   test -f "$ROOT/models/ggml-small.en.bin"
check "ollama installed"        "brew install ollama"        command -v ollama
check "ollama server running"   "brew services start ollama" curl -s --max-time 3 http://127.0.0.1:11434/api/version
check "chart model downloaded"  "ollama pull qwen2.5:7b-instruct" \
      sh -c "curl -s http://127.0.0.1:11434/api/tags | grep -q qwen2.5:7b-instruct"
check "templates present"       "restore from git: git -C '$ROOT' checkout templates/" \
      test -f "$ROOT/templates/admission.md"
check "system prompt present"   "restore from git: git -C '$ROOT' checkout prompts/" \
      test -f "$ROOT/prompts/system-chart.txt"

if [ "$FAIL" -eq 0 ]; then
  echo "All checks passed. Optional end-to-end test (takes ~30s):"
  echo "  python3 '$ROOT/scripts/chart.py' --type progress --bullets 'stable, afebrile, keep meds'"
else
  exit 1
fi
