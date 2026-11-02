# Evaluation results (25 postings)

## Fields (exact match after normalizing case, whitespace and dashes)

| Field | Accuracy |
|---|---|
| company | 19/25 (76%) |
| role_title | 19/25 (76%) |
| location | 18/25 (72%) |
| work_mode | 24/25 (96%) |
| term | 9/25 (36%) |
| deadline | 24/25 (96%) |

## Skills

| List | Precision | Recall | F1 |
|---|---|---|---|
| Required | 64% | 74% | 68% |
| Nice-to-have | 60% | 35% | 45% |
| Any list (ignores required vs nice-to-have) | 80% | 75% | 77% |

## Guardrails

- Items flagged by the grounding check: 3 (1 of them actually wrong)
- Rule fixes applied in code: 2
- Postings that failed after retry: 0
- Model calls: 25 for 25 postings (0 retries)

## Cost and latency

- Tokens: 43,955 in, 20,438 out
- Estimated cost: $0.0707 total, $0.00283 per posting
- Latency per call: median 2.3 s, max 7.5 s

## Field mismatches (review by hand: some are wording, not errors)

| Posting | Field | Label | Model |
|---|---|---|---|
| posting_01 | role_title | New Grad Tech Development Program, Software Development and Cloud Stream | New Grad Tech Development Program |
| posting_01 | term | 24-month rotation program, beginning May 2027 | 24-month |
| posting_02 | term | 4 months, January - April | January - April |
| posting_03 | company | Manulife | Manulife John Hancock |
| posting_04 | location | Markham or Oshawa | None |
| posting_04 | term | 8 or 12 months, starting January 2027 | 8 or 12 months |
| posting_05 | company | Capital One | Capital One Canada |
| posting_05 | role_title | Intern, Full Stack Software Engineer - Team Pickle | Full Stack Software Engineer - Team Pickle |
| posting_06 | location | North York, ON | Toronto, Ontario |
| posting_06 | term | 16 months, starting May 2027 | 16 Month |
| posting_07 | location | Toronto, ON | Toronto, Ontario |
| posting_07 | term | 16 months, starting May 2027 | 16 Month |
| posting_09 | company | Capital One | Capital One Canada |
| posting_09 | role_title | Intern, Full Stack Software Engineer - Team Sprout | Full Stack Software Engineer - Team Sprout |
| posting_10 | work_mode | None | hybrid |
| posting_11 | term | Winter 2027, 12 or 16 weeks | Winter 2027 |
| posting_12 | company | Capital One | Capital One Canada |
| posting_12 | role_title | Intern, Mobile Software Engineer - Team Gringotts North | Mobile Software Engineer |
| posting_13 | term | January - August 2027, 8 months | January - August 2027 |
| posting_14 | role_title | Analyste en cybersécurité, analyse de données et IA - Stage de 12 mois | Analyste en cybersécurité, analyse de données et IA |
| posting_14 | term | 12 months | 12 mois |
| posting_15 | location | Scarborough, ON | Toronto, ON |
| posting_15 | term | January 2027 - August or December 2027 (8-12 months) | 8-12 months |
| posting_16 | term | None | Internship/Cooperative |
| posting_18 | location | None | Canada |
| posting_18 | term | 12 months, start date 11/02/2026 | 12 Months |
| posting_19 | company | Capital One | Capital One Canada |
| posting_19 | role_title | Intern, Backend Software Engineer - Team Interstellar | Backend Software Engineer - Team Interstellar |
| posting_20 | location | Scarborough, ON | Toronto, ON |
| posting_20 | term | January 2027 - December 2027 (12 months) | January 2027 - December 2027 |
| posting_22 | term | 8 months preferred (Winter and Summer 2027) | 8 month preferred (Winter and Summer 2027) |
| posting_23 | location | Toronto, Calgary or Burnaby | Toronto, Calgary, Burnaby |
| posting_23 | term | 8 months, January 2027 to end of August 2027 | 8-month co-op period from January 2027 to end of August 2027 |
| posting_25 | company | Vector Institute | The Vector Institute |
| posting_25 | term | January 18, 2027 - May 7, 2027 (four months) | January 18, 2027 to May 7, 2027 |
| posting_25 | deadline | 11:59 p.m. ET on Friday, October 16, 2026 | Friday, October 16, 2026 |
| posting_26 | term | 4 months, January - April | January - April |
