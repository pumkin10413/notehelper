#!/usr/bin/env python3
"""Deterministically clean a raw OPD/EMR record dump before it reaches the model.

No model, no network — pure text processing, so it is fast, free, and auditable.
Purpose: remove system boilerplate that wastes context and distracts a 7B model,
normalize full-width characters that Taiwan hospital exports produce, and strip
obvious patient identifiers as defence-in-depth (docs/PHI-SAFETY.md).

As a filter:  python3 scripts/preprocess.py < raw.txt > clean.txt
As a module:  from preprocess import clean_record

DESIGN RULE: when in doubt, KEEP the line. Dropping a clinical fact is far worse
than leaving a noisy one. Only patterns that are unambiguously boilerplate are cut.
"""
import re
import sys

# --- lines that are pure system noise (matched on the whole stripped line) ---
NOISE_PATTERNS = [
    r"^[-=_*~#─━═╌┄┈≡\.]{3,}$",                         # separator rules (incl. box-drawing)
    r"^page\s*\d+(\s*(of|/)\s*\d+)?$",                  # Page 3 of 7
    r"^第\s*\d+\s*[頁页].*$",                            # Chinese page markers
    r"^(printed|print date|列印日期|列印時間)\b.*$",       # print timestamps
    r"^\s*\d{1,3}\s*$",                                 # a bare number on its own line
    r"^(confidential|機密).*$",
    r"^(this (report|document) .*(confidential|property).*)$",
    r"^[一-鿿]{0,10}(醫院|醫學中心|診所)\s*$",     # bare hospital-name banner
]
NOISE_RE = [re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS]

# --- identifier redaction (label-driven, so it is precise) ---
ID_LABELS = (
    r"(?:patient\s*name|name|chart\s*(?:no|number)|medical\s*record\s*(?:no|number)|"
    r"mrn|id\s*(?:no|number)?|national\s*id|姓\s*名|病歷號(?:碼)?|身分證(?:字號)?|"
    r"身份證(?:字號)?|病人姓名)"
)
ID_LINE_RE = re.compile(r"^\s*%s\s*[:：]\s*\S.*$" % ID_LABELS, re.IGNORECASE)
ID_INLINE_RE = re.compile(r"(%s)\s*[:：]\s*[^\s,;，；|]+" % ID_LABELS, re.IGNORECASE)
TW_NATIONAL_ID_RE = re.compile(r"\b[A-Za-z][12]\d{8}\b")


def _to_halfwidth(text):
    """Full-width ASCII (Ａ-Ｚ, ０-９, ：, ％ ...) -> half-width, so labs parse cleanly.
    Leaves CJK characters and CJK-only punctuation (，。、) untouched."""
    out = []
    for ch in text:
        code = ord(ch)
        if code == 0x3000:              # ideographic space
            out.append(" ")
        elif 0xFF01 <= code <= 0xFF5E:  # full-width ASCII range
            out.append(chr(code - 0xFEE0))
        else:
            out.append(ch)
    return "".join(out)


def clean_record(text):
    """Return (cleaned_text, stats_dict)."""
    original_lines = text.splitlines()
    text = _to_halfwidth(text)
    # Normalize tabs and non-breaking spaces; strip zero-width junk.
    text = text.replace("\t", " ").replace(" ", " ")
    text = re.sub(r"[​-‏﻿]", "", text)

    kept, dropped, redacted = [], 0, 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            kept.append("")
            continue
        if any(rx.match(stripped) for rx in NOISE_RE):
            dropped += 1
            continue
        if ID_LINE_RE.match(stripped):          # a whole line that is just an identifier
            dropped += 1
            redacted += 1
            continue
        new_line, n1 = ID_INLINE_RE.subn(lambda m: m.group(1) + ": [redacted]", stripped)
        new_line, n2 = TW_NATIONAL_ID_RE.subn("[redacted]", new_line)
        redacted += n1 + n2
        kept.append(re.sub(r" {2,}", " ", new_line))

    cleaned = "\n".join(kept)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    stats = {
        "lines_in": len(original_lines),
        "lines_out": len([l for l in cleaned.splitlines() if l.strip()]),
        "lines_dropped": dropped,
        "identifiers_redacted": redacted,
        "chars_in": len(text),
        "chars_out": len(cleaned),
    }
    return cleaned, stats


if __name__ == "__main__":
    data = sys.stdin.read()
    out, st = clean_record(data)
    sys.stdout.write(out + "\n")
    sys.stderr.write(
        "preprocess: %(lines_in)d->%(lines_out)d lines, %(lines_dropped)d noise lines dropped, "
        "%(identifiers_redacted)d identifiers redacted\n" % st
    )
