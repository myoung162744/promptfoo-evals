# Results — which Claude model grades most like human raters

Run 2026-06-16. Each dataset: 50 stratified cases (`--seed 42`), graded by three
Anthropic models at `temperature: 0`. Headline metric is **Quadratic Weighted
Kappa (QWK)** between the model's overall score and the human score. Human–human
agreement on ASAP is ~0.75 — that's the bar.

Reproduce:
```bash
.venv/bin/python scripts/prepare.py --dataset all --n 50 --seed 42
for c in asap-sas asap-essays persuade ellipse; do
  npx promptfoo eval -c configs/$c-nojudge.yaml --env-file .env \
    --filter-providers anthropic -o output/$c.json
  .venv/bin/python scripts/analyze.py output/$c.json --traits
done
```

## Overall-score QWK

| Dataset (task) | Haiku 4.5 | Sonnet 4.6 | Opus 4.8 | Notes |
|---|---|---|---|---|
| **ASAP-SAS** (short answer, 0–3) | 0.718 | 0.776 | **0.783** | all near/above human bar; ~neutral bias |
| **ASAP++** (essay, sets 1–2) | 0.629 | **0.825** | 0.815 | Haiku grades lenient (+1.5) on the 2–12 scale |
| **PERSUADE 2.0** (essay, 1–6) | 0.470 | 0.520 | **0.659** | all below bar, all grade harsh (−0.7 to −1.2) |
| **ELLIPSE** (ELL essay, 1–5) | 0.608 | 0.497 | **0.718** | Sonnet collapses on ELL writing |

Parse failures: 0 for Haiku/Sonnet everywhere; Opus 1 (asap-essays) and 3
(ellipse) after the balanced-brace parser fix.

## Per-trait QWK

**ASAP++** (content / organization / word_choice / sentence_fluency / conventions):

| model | content | organization | word_choice | sentence_fluency | conventions |
|---|---|---|---|---|---|
| Haiku 4.5  | 0.668 | 0.605 | 0.515 | 0.540 | 0.312 |
| Sonnet 4.6 | 0.742 | 0.778 | 0.670 | 0.664 | 0.607 |
| Opus 4.8   | 0.827 | 0.837 | 0.766 | 0.813 | 0.638 |

**ELLIPSE** (cohesion / syntax / vocabulary / phraseology / grammar / conventions):

| model | cohesion | syntax | vocabulary | phraseology | grammar | conventions |
|---|---|---|---|---|---|---|
| Haiku 4.5  | 0.669 | 0.642 | 0.522 | 0.498 | 0.455 | 0.642 |
| Sonnet 4.6 | 0.605 | 0.548 | 0.425 | 0.430 | 0.376 | 0.417 |
| Opus 4.8   | 0.837 | 0.726 | 0.678 | 0.670 | 0.621 | 0.672 |

## Takeaways

1. **Opus 4.8 is the most reliable grader** — top or tied-top on 3 of 4
   datasets and the clear winner on the two *newer* datasets (PERSUADE, ELLIPSE);
   best per-trait agreement everywhere.
2. **Sonnet 4.6 is a strong, cheaper option for essays** — edges Opus on ASAP++
   (within noise) — **but collapses on ELLIPSE (0.497, worst)**; weak at grading
   English-language-learner writing.
3. **Haiku 4.5 is viable for short answers** (0.718, near the human bar) at the
   lowest cost; weakest on essays and over-lenient on the unusual 2–12 scale.
4. **Contamination signal.** All models agree more on the older, public
   ASAP/ASAP-SAS/ASAP++ (2012) than on PERSUADE 2.0 (2022) and ELLIPSE — on
   PERSUADE all three fall below the human bar. Trust the PERSUADE/ELLIPSE
   numbers more for real-world deployment.
5. **Error direction.** On free-response essays all models grade *harsher* than
   humans (negative mean signed error) — they'd under-score students without
   calibration.

## Caveats

- **Anthropic-only run.** `openai:gpt-5.1`/`gpt-5.1-mini` (billing inactive) and
  `google:gemini-3-pro-preview` (free-tier `limit: 0`) couldn't run;
  `google:gemini-2.5-flash` was excluded because free-tier rate limits made a
  full 200-call run intractable. Cross-provider comparison needs active billing.
- **`feedback_quality` judge skipped.** promptfoo v0.121.15 throws
  `RangeError: Maximum call stack size exceeded` when an Anthropic provider is
  used as an `llm-rubric` judge. The `configs/*-nojudge.yaml` variants drop that
  assertion; QWK is judge-independent so rankings are unaffected.
- **n=50, stratified** → QWK confidence ±~0.1; treat gaps under 0.1 as ties
  (e.g. Sonnet vs Opus on ASAP++). Re-run with `--n 150` to tighten.
- Stratified sampling flattens the natural score distribution; QWK is comparable
  across models (identical cases) but is not "accuracy on the dataset."
