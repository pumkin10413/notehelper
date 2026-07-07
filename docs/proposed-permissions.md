# Proposed .claude/settings.json (user must apply manually)

Claude cannot write its own permission settings (correctly blocked). To make future sessions
run without permission prompts — especially important for smaller models doing routine work —
review the JSON below and, if you agree, paste it into `.claude/settings.json` in this repo
(create the file), or run the `/fewer-permission-prompts` skill in a session and confirm its
suggestions.

The `deny` on WebFetch/WebSearch is deliberate: sessions in this repo have no legitimate need
to reach the web (PHI-SAFETY rule 1), so blocking it at the harness level converts a policy
into a guarantee.

```json
{
  "permissions": {
    "allow": [
      "Bash(bash scripts/doctor.sh)",
      "Bash(bash scripts/dictate.sh:*)",
      "Bash(bash scripts/voice-chart.sh:*)",
      "Bash(python3 scripts/chart.py:*)",
      "Bash(python3 eval/run_eval.py:*)",
      "Bash(python3 app/server.py:*)",
      "Bash(ollama list:*)",
      "Bash(curl -s http://127.0.0.1:11434/*)",
      "Bash(curl -s http://127.0.0.1:8765/*)",
      "Bash(brew services start ollama)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git log:*)",
      "Bash(git diff:*)",
      "Bash(git status)"
    ],
    "deny": [
      "WebFetch",
      "WebSearch"
    ]
  }
}
```
