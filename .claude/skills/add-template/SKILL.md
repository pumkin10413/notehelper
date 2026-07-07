---
name: add-template
description: Add or update a chart template from the user's real (de-identified) hospital chart sample. Use when the user provides a sample chart, wants a new chart type supported, or wants an existing template to match their hospital's format.
---

# Add or update a template from a sample

Follow `templates/README.md` exactly. Condensed procedure:

1. **PHI gate (mandatory, do this before anything else):** scan the sample against the
   checklist in docs/PHI-SAFETY.md (names, chart numbers, IDs, exact dates, staff names...).
   If anything identifying is present, STOP — show the user each item and ask for a cleaned
   version. Do not save the dirty text anywhere, including temp files.
2. Save the clean sample as `samples/<type>-<nn>.md` (increment nn; never overwrite).
3. Back up the existing template: `cp templates/<type>.md templates/<type>.md.bak-$(date +%Y%m%d)`
   (skip if it's a brand-new type).
4. Write the template in the three-part format defined in templates/README.md
   (NAME/STYLE header, `---`, skeleton with `[bracketed slots]`, `---`, RULES).
   Keep the sample's exact headers, ordering, and recurring fixed phrases verbatim.
   Every RULES section must include a no-invented-values rule for that chart type.
5. Add one eval case in `eval/cases/<type>-<nn>.json` derived from the sample
   (format in eval/README.md).
6. Run `python3 eval/run_eval.py` — all cases must pass before you're done. If the new
   template breaks an old case for the same type because the format legitimately changed,
   update that case's `must_contain` to the new format and note it to the user.
7. Tell the user the template is live in both CLI (`--type <type>`) and the web app dropdown
   (it reads templates/ automatically; no code change needed).
