#!/usr/bin/env python3
"""Generate a formatted chart from bullets, or from a raw OPD/EMR record dump.

Usage:
  # short bullets (one stage)
  python3 scripts/chart.py --type admission --bullets "65M, DM/HTN, fever 3 days ..."

  # raw multi-visit OPD record + exam reports (two stages: extract -> write)
  python3 scripts/chart.py --type pi --raw --file opd_dump.txt
  pbpaste | python3 scripts/chart.py --type pi --raw --show-timeline

Stdlib only, Python 3.9 compatible. All processing is local (Ollama at 127.0.0.1).
If anything fails, run: bash scripts/doctor.sh

WHY TWO STAGES (see docs/OPD-RECORDS.md): a 7B model given a long messy record AND a
formatting task at once drops facts. Stage A extracts a structured timeline (extraction
only — small models are reliable at this); stage B writes prose from that short clean
timeline. The timeline is also auditable: --show-timeline lets you verify nothing was
lost before you trust the prose.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocess import clean_record  # noqa: E402

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MODEL = "qwen2.5:7b-instruct"
DEFAULT_URL = "http://127.0.0.1:11434"


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def list_templates():
    tdir = os.path.join(PROJECT_ROOT, "templates")
    return sorted(
        f[:-3] for f in os.listdir(tdir)
        if f.endswith(".md") and f != "README.md" and ".bak" not in f
    )


def pick_num_ctx(*texts):
    """Choose a context window big enough for the input.

    Ollama silently discards the OLDEST tokens when the prompt exceeds num_ctx, which on a
    multi-visit record means the earliest visits vanish without any error. Sizing up front
    is what prevents that. ~3 chars/token is a deliberate under-estimate of token length
    (medical abbreviations and numbers tokenize poorly), so we err toward a larger window.
    """
    approx_tokens = sum(len(t) for t in texts) / 3.0
    needed = approx_tokens + 1500          # headroom for the generated answer
    for size in (8192, 16384, 32768):
        if needed <= size:
            return size
    return 32768                            # qwen2.5 ceiling we support on 16 GB


def _chat(messages, model, url, timeout, num_ctx):
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        # Low temperature: this is extraction/format transformation, not creative writing.
        "options": {"temperature": 0.2, "num_ctx": num_ctx},
    }
    req = urllib.request.Request(
        url.rstrip("/") + "/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        sys.exit("ERROR: cannot reach Ollama at %s (%s).\n"
                 "Fix: run 'brew services start ollama', then 'bash scripts/doctor.sh'." % (url, e))
    content = body.get("message", {}).get("content", "").strip()
    if not content:
        sys.exit("ERROR: empty response from model. Run 'bash scripts/doctor.sh'.")
    return content


def build_messages(chart_type, bullets):
    template_path = os.path.join(PROJECT_ROOT, "templates", chart_type + ".md")
    if not os.path.exists(template_path):
        sys.exit("ERROR: no template '%s'. Available: %s"
                 % (chart_type, ", ".join(list_templates())))
    system_prompt = read_file(os.path.join(PROJECT_ROOT, "prompts", "system-chart.txt"))
    template = read_file(template_path)
    user_msg = "TEMPLATE:\n%s\n\nPHYSICIAN INPUT:\n%s" % (template, bullets.strip())
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg},
    ]


def generate(chart_type, bullets, model=DEFAULT_MODEL, url=DEFAULT_URL, timeout=300):
    """Single-stage: clean bullets -> chart. Core entry point; imported by app/server.py."""
    messages = build_messages(chart_type, bullets)
    num_ctx = pick_num_ctx(messages[0]["content"], messages[1]["content"])
    return _chat(messages, model, url, timeout, num_ctx)


def extract_timeline(raw_text, model=DEFAULT_MODEL, url=DEFAULT_URL, timeout=600):
    """Stage A: raw OPD/EMR dump -> structured clinical timeline (see prompts/system-extract.txt)."""
    system_prompt = read_file(os.path.join(PROJECT_ROOT, "prompts", "system-extract.txt"))
    user_msg = "RAW MEDICAL RECORD:\n%s" % raw_text.strip()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg},
    ]
    num_ctx = pick_num_ctx(system_prompt, user_msg)
    return _chat(messages, model, url, timeout, num_ctx)


def generate_from_raw(chart_type, raw_text, model=DEFAULT_MODEL, url=DEFAULT_URL, timeout=600):
    """Two-stage: raw record -> (chart, timeline, preprocess stats)."""
    cleaned, stats = clean_record(raw_text)
    if not cleaned.strip():
        sys.exit("ERROR: nothing left after cleaning — is the input empty or pure boilerplate?")
    timeline = extract_timeline(cleaned, model=model, url=url, timeout=timeout)
    chart = generate(chart_type, timeline, model=model, url=url, timeout=timeout)
    return chart, timeline, stats


def main():
    ap = argparse.ArgumentParser(description="bullets or raw OPD record -> formatted chart (local LLM)")
    ap.add_argument("--type", required=True, help="chart type: %s" % ", ".join(list_templates()))
    ap.add_argument("--bullets", help="bullet text inline")
    ap.add_argument("--file", help="read input from a file")
    ap.add_argument("--raw", action="store_true",
                    help="input is a raw OPD/EMR dump (multiple visits, lab/exam reports): "
                         "clean it, extract a timeline, then write the chart")
    ap.add_argument("--show-timeline", action="store_true",
                    help="with --raw, also print the intermediate timeline to stderr for auditing")
    ap.add_argument("--model", default=os.environ.get("CHART_MODEL", DEFAULT_MODEL))
    ap.add_argument("--url", default=os.environ.get("OLLAMA_URL", DEFAULT_URL))
    args = ap.parse_args()

    if args.bullets:
        text = args.bullets
    elif args.file:
        text = read_file(args.file)
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        ap.error("provide --bullets, --file, or pipe text on stdin")

    if not text.strip():
        sys.exit("ERROR: input is empty.")

    if args.raw:
        chart, timeline, stats = generate_from_raw(
            args.type, text, model=args.model, url=args.url)
        sys.stderr.write(
            "preprocess: %(lines_in)d->%(lines_out)d lines, %(lines_dropped)d noise lines dropped, "
            "%(identifiers_redacted)d identifiers redacted\n" % stats)
        if args.show_timeline:
            sys.stderr.write("----- EXTRACTED TIMELINE (verify nothing is missing) -----\n")
            sys.stderr.write(timeline + "\n----- CHART -----\n")
        print(chart)
    else:
        print(generate(args.type, text, model=args.model, url=args.url))


if __name__ == "__main__":
    main()
