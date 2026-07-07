#!/bin/bash
# Full voice-to-chart pipeline: dictate -> transcribe -> format into a chart -> stdout.
#
# Usage:
#   bash scripts/voice-chart.sh progress          # dictate, Enter to stop, get a SOAP note
#   bash scripts/voice-chart.sh admission 60      # dictate 60s, get an admission note
#
# The transcript is shown first so you can see what whisper heard; the chart follows.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

TYPE="${1:?usage: voice-chart.sh <type> [seconds]  (types: see templates/)}"
SECS="${2:-}"

TRANSCRIPT="$(bash "$ROOT/scripts/dictate.sh" $SECS)"
echo "----- TRANSCRIPT (verify before trusting the chart) -----" >&2
printf '%s\n' "$TRANSCRIPT" >&2
echo "----- CHART -----" >&2
printf '%s' "$TRANSCRIPT" | python3 "$ROOT/scripts/chart.py" --type "$TYPE"
