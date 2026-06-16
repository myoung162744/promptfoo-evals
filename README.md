# LLM Essay & Short-Answer Grading Evals

Which LLMs grade student writing most like human raters? This repo evaluates
models on four public datasets with real human scores, using
[promptfoo](https://www.promptfoo.dev/) for execution and Quadratic Weighted
Kappa (QWK) for ranking.

## Datasets

| Config | Dataset | Task | Scale | Human labels |
|---|---|---|---|---|
| `configs/asap-essays.yaml` | [ASAP++](https://lwsam.github.io/ASAP++/lrec2018.html) (sets 1–2) | Persuasive essays, grades 7–10 | traits 1–6; overall 2–12 (set 1) / 1–6 (set 2) | overall + 5 traits (content, organization, word choice, sentence fluency, conventions) |
| `configs/asap-sas.yaml` | [ASAP-SAS](https://www.kaggle.com/c/asap-sas) (sets 1, 2, 5, 6) | Short answers (science/biology) | 0–3 | overall |
| `configs/persuade.yaml` | [PERSUADE 2.0 / ASAP 2.0](https://github.com/scrosseye/ASAP_2.0) | Source-based persuasive essays, grades 6–12 | 1–6 holistic | overall |
| `configs/ellipse.yaml` | [ELLIPSE](https://github.com/scrosseye/ELLIPSE-Corpus) | English-language-learner essays | 1–5 in 0.5 steps | overall + 6 traits (cohesion, syntax, vocabulary, phraseology, grammar, conventions) |

All data is fetched from public GitHub/HuggingFace mirrors — **no Kaggle
account needed**. ASAP-SAS comes via the [AERA paper repo](https://github.com/lijiazheng99/aera)
(original answers, scores, and official question/rubric text).

## Setup

```bash
# one-time
python3 -m venv .venv && .venv/bin/pip install pandas pyyaml numpy pypdf
npm install                      # installs promptfoo locally

./scripts/download.sh            # fetch raw datasets (~80 MB)
.venv/bin/python scripts/prepare.py --dataset all --n 50 --seed 42
```

API keys live in `.env` (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`).

> **Provider availability (verified 2026-06-12 on this machine's keys).** Some
> planned providers are commented out in every `configs/*.yaml` because the
> accounts can't reach them yet. Re-enable the commented `- id:` lines once
> billing is sorted:
> | Provider | Status | Why |
> |---|---|---|
> | Anthropic (opus 4.8, sonnet 4.6, haiku 4.5) | ✅ enabled | working |
> | `google:gemini-2.5-flash` | ✅ enabled | works on free tier |
> | `google:gemini-3-pro-preview` | ❌ commented out | Google key is free-tier; `limit: 0` for gemini-3-pro (needs paid AI Studio tier) |
> | `openai:gpt-5.1`, `gpt-5.1-mini` | ❌ commented out | key returns `429 billing_not_active` |
>
> The `feedback_quality` judge is temporarily `google:gemini-2.5-flash` (the
> only non-Anthropic model currently reachable). Once OpenAI billing is active,
> switch it back to `openai:gpt-5.1` — a held-out judge avoids the
> self-preference confound where a model rates its own family's output.

## Running

```bash
# cheap pipeline sanity check (5 synthetic essays, 2 budget models)
npx promptfoo eval --env-file .env -o output/synthetic.json

# real evals — one config per dataset
npx promptfoo eval -c configs/asap-essays.yaml --env-file .env -o output/asap-essays.json
npx promptfoo eval -c configs/asap-sas.yaml    --env-file .env -o output/asap-sas.json
npx promptfoo eval -c configs/persuade.yaml    --env-file .env -o output/persuade.json
npx promptfoo eval -c configs/ellipse.yaml     --env-file .env -o output/ellipse.json

npx promptfoo view                # browse transcripts side by side
```

Reruns reuse the response cache, so a run interrupted by rate limits/503s can
simply be run again to fill the gaps.

## Ranking models

Promptfoo pass-rates are per-assertion; the field-standard agreement metric is
**QWK** (human–human QWK on ASAP is ~0.75 — that's the bar):

```bash
.venv/bin/python scripts/analyze.py output/asap-essays.json --traits
```

Reports per model: QWK, exact agreement, adjacent agreement (±1, or ±0.5 for
ELLIPSE), **mean signed error** (positive = model grades more leniently than
humans), Pearson r, and parse-failure rate. `--traits` adds per-trait QWK.

### What the in-run assertions measure

| Metric | Meaning |
|---|---|
| `valid_json` | Output parsed as JSON with a numeric `overall` (format compliance) |
| `exact_match` | Overall score equals the human score exactly (informational — expect misses) |
| `adjacent_match` | Within tolerance of human score |
| `traits_adjacent` | Fraction of trait scores within tolerance |
| `feedback_quality` | LLM judge on evidence/feedback quality (secondary; judge has self-preference bias toward its own family) |

A test shows "failed" if *any* assertion fails, and `exact_match` misses often
— that's the phenomenon being measured, not a pipeline error. Judge results
and QWK are what rank models.

## Scaling up

The 50-case smoke test gives noisy QWK (±~0.1); rankings firm up at 150+.

```bash
.venv/bin/python scripts/prepare.py --dataset all --n 150 --seed 42
```

Sampling is stratified: even across essay sets/questions, round-robin across
human score levels, so low/mid/high scores are all represented.

## Interpretation caveats

- **Contamination:** ASAP/ASAP-SAS are public since 2012 with published
  scores; models may have partially memorized them. PERSUADE 2.0 (2022) and
  ELLIPSE are newer. If a model does much better on ASAP than PERSUADE,
  suspect contamination.
- **Compare within a dataset, not across** — each has different human-rater
  reliability and scales.
- **ASAP anonymization tokens** (`@PERSON1`, `@LOCATION2`) are left in essays;
  the grader prompt tells models not to penalize them.
- **PERSUADE prompts:** only the two prompts with machine-readable source PDFs
  are sampled (electoral college, car-free cities). The other five source PDFs
  are scans; OCR them into `datasets/raw/asap2/source_txt/` and extend
  `PERSUADE_SOURCES` in `scripts/prepare.py` to include them.
- The stratified sample flattens the natural score distribution; QWK is still
  comparable across models (all see identical cases) but don't quote it as
  "accuracy on the dataset."

## Layout

```
configs/               # one promptfoo config per dataset (edit provider list in all four)
prompts/               # JSON-output grader prompts (essay + short answer)
rubrics/               # extracted official rubric text (inlined into test cases)
evals/                 # JS assertions (parse_output.js shared) — QWK lives in scripts/analyze.py
scripts/download.sh    # raw data from no-auth mirrors
scripts/prepare.py     # stratified sampling -> test-inputs/generated/*.yaml
scripts/analyze.py     # QWK / agreement / bias tables from promptfoo -o JSON
test-inputs/essays.yaml          # 5 synthetic essays (cheap sanity check)
test-inputs/generated/           # generated test cases (reproducible; gitignored)
datasets/raw/                    # downloads (gitignored)
```
