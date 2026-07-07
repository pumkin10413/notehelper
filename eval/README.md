# Eval — regression tests for chart quality

**When to run:** after ANY edit to `prompts/`, `templates/`, or a model change. Takes 1-3 min.

```bash
python3 eval/run_eval.py            # all cases
python3 eval/run_eval.py admission-1  # one case
```

Exit 0 = safe to keep the change. Exit 1 = the change broke something: **revert it**
(restore the `.bak-` file or `git checkout` the edited file), then try a different edit.
Never "fix" a failure by deleting or weakening the eval case — cases encode past bugs and
the no-hallucination guarantee. The only valid reason to edit a case is that the *template*
legitimately changed (e.g. user replaced it with their hospital's real format); update the
case's `must_contain` to the new format in the same commit.

## Automatic checks (every case)
- **A2 no invented numbers** is the most important check in this repo: every number in the
  output must exist in the input bullets or the template. This catches hallucinated vitals,
  labs, and doses. If A2 fails, the prompt/template change is dangerous — revert.

## Adding a case
1. Copy an existing `cases/*.json`, keep it de-identified (docs/PHI-SAFETY.md).
2. `must_contain`: 4-8 substrings — section headers plus key clinical facts that MUST survive.
3. `must_not_contain`: things that would indicate leakage of template placeholders
   (e.g. "[age]"), meta-text, or facts absent from the bullets.
4. Add one case per real-world failure the user reports: reproduce the bad input, encode the
   expected behavior. This is how the system learns permanently.

## Judgment checks the script cannot do (do these by reading one output)
After a big prompt/template change, generate one admission note and personally verify:
- Present Illness is prose (not bullets) and chronological.
- Nothing in Impression exceeds what the bullets stated.
- Missing-data fields say "not recorded" / "___ (fill in)" rather than plausible inventions.
