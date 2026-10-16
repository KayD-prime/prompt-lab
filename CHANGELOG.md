# Change log

Every change to a prompt gets a line here: what changed, why, and what the suite said before and after.

## triage

### v1 · 2026-10-16
- First version: five categories, one-sentence summary, `Category:` / `Summary:` format.
- Suite: 5 cases, 5 pass on the practice server. On the real model (openai/gpt-oss-20b, two runs over ten emails) the
  sarcastic email (6) was read as praise both times, the praise email (5) flipped between Other and Product, and the
  wholesale enquiry (9) was labelled Product both times.
