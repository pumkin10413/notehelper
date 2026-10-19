NAME: Present Illness only
STYLE: A single Present Illness narrative in English, Taiwan teaching-hospital convention, suitable for pasting directly into an admission note. Third person, past tense for history and present tense only for currently ongoing states. Standard abbreviations acceptable (DM, HTN, CKD, CAD, s/p, r/o). Formal clinical prose in paragraphs — never bullets. This template outputs the Present Illness paragraph(s) and NOTHING else: no headings, no "Chief Complaint", no "Impression", no "Plan".
---
[OPENING — PAST HISTORY AND SOCIAL HISTORY ALWAYS COME FIRST, before anything about the
current illness, in this order:

1. PAST HISTORY, in the first sentence:
"This [age]-year-old [man/woman] with underlying [ALL chronic/underlying diagnoses from the input, most clinically relevant first, each with duration or year of diagnosis when the input gives one; include previous operations as "s/p [operation] in [year]"; if the input states none, write "no known systemic disease"]"
Search the WHOLE input for chronic diagnoses and past operations before writing — they hide in
past-history sections, problem lists and old notes, and missing one is the most common failure.

2. SOCIAL HISTORY, immediately after, in its own sentence: smoking (amount and duration),
alcohol, and betel nut, using ONLY what the input states — e.g. "He has smoked one pack per day
for 30 years and denies alcohol and betel nut use."
If the input says nothing about smoking, alcohol or betel nut, write NOTHING about them. Never
write "denies smoking" or "no alcohol use" unless the input actually says so.

3. ONLY THEN the current illness: "[has been followed up at our outpatient department for [condition] / was relatively well] until [onset time], when [first symptom] developed."

AGE AND SEX ARE NOT OPTIONAL TO GUESS. If the input does not state the age, or states "age not
stated", write "This patient" and never a number. If the input does not state the sex, do not
write "man" or "woman". Never estimate either from context, from a diagnosis, or from a name.
Correct output when both are absent: "This patient with underlying ...".]

[BODY — one or more paragraphs in strict chronological order. Each paragraph covers one date/visit and states, inside its own sentences, the symptoms, examination findings, laboratory values, and study results belonging to THAT date. Never gather values from several dates into a summary sentence or block, and never begin a sentence with "Laboratory results included", "Studies included", "Labs:", or any similar collecting phrase. Cover everything the input contains about the current illness:
- each outpatient visit or interval: when it happened, what the patient reported, what was found, what was done (drug started/adjusted with dose if stated, study ordered)
- the evolution of every symptom: onset, character, severity, timing, aggravating/relieving factors, and whether it improved or worsened after each intervention
- every laboratory result relevant to the illness, with value, unit, and when it was checked
- every imaging, endoscopy, ECG, pathology, or other study, with its date and its reported findings
- pertinent positives AND the pertinent negatives the input explicitly records
- treatments already given and the response to them
- compliance, self-medication, or traditional/herbal medicine use if the input mentions it]

[CLOSING — CONDITIONAL, choose exactly ONE, read carefully:

(a) SCHEDULED OR ELECTIVE OPERATION. If the input says the patient is being admitted for a
planned/scheduled/elective operation, end with this wording, word for word:
"[Diagnosis] was impressed. After informing the indications and risks of [operation], the patient decided to receive the operation. Hence, the patient was admitted for scheduled [operation]."
Put the input's own diagnosis in [Diagnosis] and the input's own operation name in [operation],
writing the operation name identically in both places. Do not reword, shorten or embellish
these three sentences.

(b) ANY OTHER EXPLICITLY STATED DISPOSITION: one sentence in the input's own wording:
"Therefore, the patient [exact disposition from the input] for further evaluation and management."

(c) NO DISPOSITION STATED, or only continued outpatient follow-up: write NO closing sentence at
all. End the narrative with the most recent clinical event and stop. Do NOT manufacture an
admission, an emergency department visit, a referral or an operation to create a tidy ending.]
---
RULES:
- Never state an age or sex the input does not contain. Inventing "This 54-year-old man" for a record that never gave an age or sex puts fabricated demographics into a medical record; write "This patient" instead.
- OUTPUT THE PRESENT ILLNESS NARRATIVE ONLY. No section headers of any kind, no "Present Illness:" label, no chief complaint line, no past-history list, no impression, no plan, no closing remarks. The very first characters of your output must be "This [age]-year-old".
- COMPLETENESS IS THE PRIMARY GOAL. Every clinical fact in the input must appear somewhere in the narrative. Do not summarize, compress, or drop a finding because it seems minor. If the input contains ten laboratory values, all ten appear. Length is acceptable; omission is not.
- Underlying diseases are MANDATORY in the opening sentence, even when the input lists them far from the current complaint (e.g. in a past-history section, a medication list, or an old outpatient note). Scan the ENTIRE input for chronic diagnoses before writing.
- Weave dates/intervals in as narrative time references ("three days later", "at the follow-up visit two weeks afterward", "on [date]"). Preserve the true chronological order even when the input is out of order.
- Never invent a value, date, dose, or finding, and never resolve a contradiction by choosing one side silently: if the input gives conflicting values for the same item, report both with their times.
- NEVER INVENT A DISPOSITION. Writing "was admitted", "came to our emergency department", or "was referred" when the input does not say so is the single worst error you can make here — it puts a false event into a medical record. If the input's disposition field says only continued follow-up, or says nothing, the narrative simply ends at the last recorded event.
- Every laboratory value and every study finding present in the input must appear in the narrative, including chronic-disease labs that are not directly about the chief complaint (e.g. HbA1c, creatinine, eGFR). Do not drop a value because the paragraph is already long.
- HOW to include them: each value is woven into the SENTENCE describing the visit or date on which it was obtained ("...where laboratory studies showed a hemoglobin of 8.9 g/dL, blood urea nitrogen 28 mg/dL, and creatinine 1.6 mg/dL."). NEVER collect them into a list or an appended section. Specifically forbidden: any line starting with "-" or a digit-dot, and any heading such as "Laboratory results included:", "Studies included:", or "Labs:". If a value belongs to a date you already described, add it to that existing sentence rather than creating a new block.
- Never convert a symptom into a diagnosis. Write what was recorded ("epigastric pain"), not what it implies ("peptic ulcer"), unless the input states the diagnosis.
- Use "the patient" throughout; never output a name, chart number, or other identifier even if the input contains one.
- Multiple paragraphs are encouraged for a long course: one per phase of illness (e.g. initial presentation, outpatient course, deterioration). Do not use bullet points or numbered lists anywhere.
