#!/usr/bin/env python3
"""Regression eval for the chart pipeline. Run after ANY change to prompts/, templates/,
or the model. Stdlib only.

Usage:
  python3 eval/run_eval.py            # run all cases in eval/cases/
  python3 eval/run_eval.py progress-1 # run one case

Each case is eval/cases/<name>.json:
{
  "type": "progress",                       // template name
  "bullets": "...",                         // input
  "must_contain": ["S:", "BP 128/76"],      // literal substrings (case-insensitive)
  "must_not_contain": ["Here is", "```"]    // literal substrings that must be absent
}

Automatic checks applied to every case (no need to declare them):
  A1 non-empty output
  A2 no invented numbers: every number in the output must appear in the bullets or template
  A3 no meta-text: output does not start with "Here", "Sure", "Below", or a code fence

Exit code 0 = all pass. Nonzero = failures listed; DO NOT ship the change that caused them.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import chart  # noqa: E402

NUM_RE = re.compile(r"\d+(?:\.\d+)?")


def numbers_in(text):
    return set(NUM_RE.findall(text))


def run_case(path):
    with open(path, encoding="utf-8") as f:
        case = json.load(f)
    name = os.path.basename(path)[:-5]
    out = chart.generate(case["type"], case["bullets"])
    template = open(os.path.join(ROOT, "templates", case["type"] + ".md"), encoding="utf-8").read()
    failures = []

    if not out.strip():
        failures.append("A1 empty output")
    allowed = numbers_in(case["bullets"]) | numbers_in(template)
    # List-item numerals ("1.", "2)") at line start are enumeration, not clinical facts.
    out_for_numbers = re.sub(r"(?m)^\s*\d+[.)]\s", "", out)
    invented = numbers_in(out_for_numbers) - allowed
    if invented:
        failures.append("A2 invented numbers: %s" % sorted(invented))
    if re.match(r"^\s*(here|sure|below|certainly|```)", out, re.IGNORECASE):
        failures.append("A3 meta-text preamble: %r" % out[:60])

    low = out.lower()
    for s in case.get("must_contain", []):
        if s.lower() not in low:
            failures.append("missing required text: %r" % s)
    for s in case.get("must_not_contain", []):
        if s.lower() in low:
            failures.append("forbidden text present: %r" % s)

    status = "PASS" if not failures else "FAIL"
    print("%s  %s" % (status, name))
    for fmsg in failures:
        print("      - " + fmsg)
    if failures:
        print("      --- output was: ---")
        print("      " + out[:1500].replace("\n", "\n      "))
    return not failures


def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else "*"
    paths = sorted(glob.glob(os.path.join(ROOT, "eval", "cases", pattern + ".json")))
    if not paths:
        sys.exit("no eval cases match %r" % pattern)
    print("Running %d case(s) against model (each takes ~10-40s)..." % len(paths))
    results = [run_case(p) for p in paths]
    print("%d/%d passed" % (sum(results), len(results)))
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
