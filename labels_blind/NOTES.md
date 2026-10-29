# Labeling notes

Blind-labeled 8 postings (03, 07, 11, 15, 17, 20, 22, 23) using only LABELING.md,
then compared with AI-drafted labels for the same postings.

## Agreement
- Fields: 41/48 exact (85%); 45/48 on meaning (94%). Most mismatches were wording
  differences in `term`.
- Skills: 43 shared (65 mine, 58 AI's), about 70% overlap.
- Almost all skill disagreements came from gaps in LABELING.md, not from misreading postings.

## Decisions from the comparison
1. **Vague skills (03, 07, 11, 15, 17, 20, 22, 23).** I labeled activities and categories
   ("data preparation", "IT concepts", "IDE", "cloud platform", "AI", "previous internship")
   that fail the resume test. Added explicit "does not count" examples to the guidelines.
2. **22 Sun Life: "What Makes You a Great Fit."** I put these skills in nice-to-have.
   That header isn't an optional marker, so they're required. My error.
3. **23 Clio: "What you may have."** Decided this means preferred → nice-to-have.
   (The AI labeled them required.) Added "What you may have" to the optional markers.
4. **23 Clio location.** I used the company's office list instead of the job's hub
   offices (Toronto, Calgary, Burnaby). My error. New rule: use the job's own locations.
5. **11 Harvey work_mode.** "Able to work from our Toronto office" doesn't explicitly
   say onsite, so null. (The AI inferred onsite.) Kept my label; the rule now says don't infer.
6. **20 Hitachi typos.** I copied "JavaScripts" and "Microsoft Azures". New rule: fix obvious typos.
7. **Missed skills.** 15: "source control" → version control. 07: Total Quality
   Management (under Preferred Skills). Fair catches by the AI.

8. **Skills named in job duties** (03 LLMs, 17 test automation, 22 Atlassian,
   Planview, Wrike, Agile): decided to count them as required. The tool exists to
   show what to learn, and duties name the tools the team actually uses.

## Reconciliation
- Final labels (labels/) = AI drafts with all rules above applied; 25 postings
  (24 dropped as a duplicate of 01).
- Changes this required on the AI drafts: 11 work_mode onsite → null;
  23 data structures, algorithms, SQL moved to nice-to-have ("What you may have").
- My blind labels stay unchanged in labels_blind/ as the record of the agreement check.
