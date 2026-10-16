# prompt-lab

A small, plain tool for treating prompts like code: each prompt is a file, each expectation is a test case, and
one command runs every case and tells you what broke. It is the working repository for the LearnDime course
**Prompting as a Discipline** (AI Analyst, Core 1), and it works on its own.

## What is in here

| Folder | What it holds |
|---|---|
| `prompts/` | One Markdown file per prompt, with a `## System` part, a `## User` part and `{{placeholders}}` |
| `cases/` | One JSON file per prompt: the inputs to try and what a good answer must contain |
| `inputs/` | The data the cases point at. `emails.csv` is ten customer emails from a homeware shop's inbox |
| `tests/` | The pytest file that turns every case into a test |
| `promptlab/` | The tool itself: load a prompt, call the model, check the answer, save the run |
| `practice/` | A pretend model server that answers from a table, so the suite runs free and offline |
| `.github/workflows/` | The GitHub Actions job that runs the suite on every push |

## Set up (once)

You need Python 3.11 or newer and Git. Clone, install, and copy the settings file:

```
git clone https://github.com/KayD-prime/prompt-lab.git
cd prompt-lab
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS
pip install -r requirements.txt
copy .env.example .env          # Windows
cp .env.example .env            # macOS
```

`.env` holds the model settings. Leave it as it is to use the free practice server. To use a real model, put your key in
`OPENAI_API_KEY` and set `PROMPTLAB_PRACTICE=0`. The defaults point at Groq's free tier with `openai/gpt-oss-20b`;
any OpenAI-compatible endpoint works, including Ollama on your own machine. `.env` is ignored by Git, so the key never
leaves your computer.

## Run the suite

```
python -m promptlab run triage          # every case for the triage prompt, PASS / FAIL per case
python -m promptlab run triage 3 6      # just cases 3 and 6
python -m promptlab show triage 6       # print the filled prompt and the model's answer for one input
python -m pytest -q                     # the same cases as tests, the way CI runs them
```

Runs use temperature 0 unless `.env` says otherwise, so a different answer means the prompt changed, not the dice.
Every run is saved under `runs/` (ignored by Git) with the model name, token counts and the full answers.

## Write a case

A case is a JSON object in `cases/<prompt>.json`:

```json
{"id": 6, "expect": {"category": "Delivery", "not_mentions": ["pleased", "working well"]},
 "note": "sarcasm: v1 read 'third time this month' as praise"}
```

`id` is a row of `inputs/emails.csv` (or give your own `"input": {"email": "..."}`). `expect` lists checks:

| Check | Passes when |
|---|---|
| `format: ["Category", "Summary"]` | the answer has those `Key:` lines |
| `category: "Billing"` / `category_in: [...]` | the Category line matches |
| `equals: {"Urgency": "High"}` | any named line matches a value |
| `mentions: ["refund"]` / `not_mentions: [...]` | the summary does, or does not, contain each word |
| `one_sentence: true` / `max_words: 25` | the summary's length is right (on an answer with no Summary: line, max_words counts the whole answer) |
| `is_json: true` / `regex: "..."` | the answer parses as JSON, or matches a pattern |

Checks are mechanical on purpose. They cannot tell you an answer is good; they tell you when it stops having the
properties you decided a good answer has.

## The practice server

`practice/practice_models.py` speaks the Chat Completions API and answers the ten emails from a table. It reacts to
the prompt the way the real model did in our recorded runs: it misreads the sarcastic email unless the prompt mentions
tone, it flips the praise email between Other and Product unless the prompt says what Other covers, and it calls the
wholesale enquiry a Product question unless the prompt says sales enquiries are Other. So the course's story holds
without a key, and the real model is for the moments that matter.

## Branches

- `main` is where the course starts: the tool, triage v1 and five cases.
- `course-finished` is where it ends: ten cases, triage v2, the urgency prompt and a change log. The commit
  "triage v2: system role, category definitions, rules and three examples" is the first version that passed every
  case; in Module 5 you tag it `triage-v2` in your own clone.
- `tidy-prompt` is a change that looked harmless and broke a case. The course uses it to practise reading a failed
  run and rolling back.
