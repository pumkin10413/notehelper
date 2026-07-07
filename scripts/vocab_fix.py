#!/usr/bin/env python3
"""Apply prompts/vocab-corrections.txt (wrong => right, case-insensitive) to text.

As a filter:            echo "check the a fib" | python3 scripts/vocab_fix.py
As a module (server):   from vocab_fix import apply_corrections
"""
import os
import re
import sys

VOCAB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "prompts", "vocab-corrections.txt",
)


def apply_corrections(text, vocab_path=VOCAB_PATH):
    if not os.path.exists(vocab_path):
        return text
    with open(vocab_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=>" not in line:
                continue
            wrong, right = [s.strip() for s in line.split("=>", 1)]
            if wrong:
                text = re.sub(re.escape(wrong), right, text, flags=re.IGNORECASE)
    return text


if __name__ == "__main__":
    sys.stdout.write(apply_corrections(sys.stdin.read()))
