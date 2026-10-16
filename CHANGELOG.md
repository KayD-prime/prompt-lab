# Change log

Every change to a prompt gets a line here: what changed, why, and what the suite said before and after.

## triage

### v1 · 2026-10-16
- First version: five categories, one-sentence summary, `Category:` / `Summary:` format.
- Suite: 5 cases, 5 pass on the practice server. On the real model (openai/gpt-oss-20b) at the default temperature,
  two runs over ten emails: the sarcastic email (6) was read as praise both times, the praise email (5) flipped between
  Other and Product, and the wholesale enquiry (9) was labelled Product both times. At temperature 0, cases 2, 6 and 9
  fail every run (the order number #4502 is dropped from the summary).

### v2 · 2026-10-16
- Split the prompt into a system part (role, category definitions, rules) and a user part (three labelled examples,
  the email, the format). Rules for tone, one category only, several problems in one email, order numbers, quoted
  threads and language.
- Suite: 10 cases. Before: v1 passed 7 of 10 at temperature 0 (2, 6 and 9 fail). After: 10 of 10 on the practice
  server and in three real runs.
- With two examples and no sarcasm rule, case 6 still failed in both real runs; a sarcastic example and the tone rule
  fixed it. A first wording of the refund rule made the model answer "Product, Billing" on case 3; "pick one category
  only, never two" fixed that.

### v3 · 2026-10-16
- Shortened the prompt: removed the tone rule and the third example to save tokens.

## urgency

### v1 · 2026-10-16
- New prompt: High / Medium / Low with a one-sentence reason. 5 cases; 5 pass on the practice server and in three
  real runs. A looser first wording rated the double charge and the locked account Medium.
- tests/test_prompts.py now runs every prompt in the library; tests/test_triage.py is gone.
