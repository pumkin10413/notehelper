#!/usr/bin/env python3
"""Generate a formatted chart from rough bullets using a local Ollama model.

Usage:
  python3 scripts/chart.py --type admission --bullets "65M, DM/HTN, fever 3 days ..."
  python3 scripts/chart.py --type procedure --file bullets.txt
  echo "bullets..." | python3 scripts/chart.py --type consult

Stdlib only, Python 3.9 compatible. All processing is local (Ollama at 127.0.0.1).
If anything fails, run: bash scripts/doctor.sh
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

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
    """Core entry point; also imported by app/server.py."""
    payload = {
        "model": model,
        "messages": build_messages(chart_type, bullets),
        "stream": False,
        # Low temperature: this is format transformation, not creative writing.
        "options": {"temperature": 0.2, "num_ctx": 8192},
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


def main():
    ap = argparse.ArgumentParser(description="bullets -> formatted chart (local LLM)")
    ap.add_argument("--type", required=True, help="chart type: %s" % ", ".join(list_templates()))
    ap.add_argument("--bullets", help="bullet text inline")
    ap.add_argument("--file", help="read bullets from a file")
    ap.add_argument("--model", default=os.environ.get("CHART_MODEL", DEFAULT_MODEL))
    ap.add_argument("--url", default=os.environ.get("OLLAMA_URL", DEFAULT_URL))
    args = ap.parse_args()

    if args.bullets:
        bullets = args.bullets
    elif args.file:
        bullets = read_file(args.file)
    elif not sys.stdin.isatty():
        bullets = sys.stdin.read()
    else:
        ap.error("provide --bullets, --file, or pipe text on stdin")

    if not bullets.strip():
        sys.exit("ERROR: input is empty.")

    print(generate(args.type, bullets, model=args.model, url=args.url))


if __name__ == "__main__":
    main()
