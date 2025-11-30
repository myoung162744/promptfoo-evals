# Essay Grading Evaluation - Setup Complete ✓

Your rubric-based essay evaluation is now configured and ready to run!

## What Was Created

### 1. Essay Grading Prompt
**File:** [prompts/essay_grader.txt](prompts/essay_grader.txt)

This prompt instructs the model to:
- Grade essays according to a provided rubric
- Score four dimensions: Content, Organization, Word Choice, Conventions (1-6 scale)
- Provide specific evidence from the essay
- Give constructive feedback to students

### 2. Test Cases with Sample Essays
**File:** [test-inputs/essays.yaml](test-inputs/essays.yaml)

Contains **5 sample essays** mimicking the ASAP dataset format:
- Grade 8 narrative (high quality, score 5)
- Grade 7 persuasive (medium quality, score 4)
- Grade 9 expository (low-medium quality, score 3)
- Grade 10 source-dependent (high quality, score 6)
- Grade 7 narrative (low quality, score 2)

Each includes:
- Essay prompt and rubric
- Student essay text
- Human overall score (1-6)
- Human trait-specific scores (content, organization, word choice, conventions)

### 3. Essay-Specific Evaluations
**File:** [evals/essay-grading.yaml](evals/essay-grading.yaml)

Contains **7 assertions** that check:

**Score Accuracy:**
1. Overall score within ±1 of human score
2. Content score within ±1
3. Organization score within ±1
4. Word Choice score within ±1
5. Conventions score within ±1

**Quality Checks:**
6. LLM judge evaluates reasoning quality and feedback usefulness
7. Format validation (all required sections present)

### 4. Updated Configuration
**File:** [promptfooconfig.yaml](promptfooconfig.yaml)

Updated to:
- Include essay grading prompt, tests, and assertions
- Compare **3 models**: GPT-4o-mini, GPT-4o, and Claude Sonnet 4
- Increase max_tokens to 1000 (essays need longer responses)

### 5. ASAP Dataset Guide
**File:** [ASAP-dataset-guide.md](ASAP-dataset-guide.md)

Comprehensive guide for:
- Downloading the real ASAP/ASAP++ datasets
- Converting CSV data to Promptfoo YAML format
- Scaling from 5 sample essays to hundreds of real essays
- Understanding the 8 different essay sets and scoring scales

## How to Run Your Evaluation

### Quick Start (With Sample Essays)

```bash
# Run the evaluation
npx promptfoo eval

# View results in the UI
npx promptfoo view
```

This will test all 3 models (GPT-4o-mini, GPT-4o, Claude Sonnet 4) on the 5 sample essays.

### What You'll See

The evaluation will show you:

1. **Score Accuracy**: How close each model's scores match human scores
2. **Trait-Level Performance**: Which models best match humans on Content vs Organization vs Word Choice, etc.
3. **Reasoning Quality**: Whether the model provides good justifications
4. **Model Comparison**: Side-by-side comparison of all 3 models

### Expected Results

For the **5 sample essays**, you should see:

- **Overall score matches** on most essays (±1 tolerance is generous)
- **Higher scores** on the high-quality essays (scores 5-6)
- **Lower scores** on the low-quality essays (scores 2-3)
- **Detailed feedback** citing specific examples from each essay

## What's Being Measured

Your evaluation implements the **two-layer LLM judging** approach:

### Layer 1: Model Under Test (Grader)
- GPT-4o-mini, GPT-4o, or Claude Sonnet 4
- Grades the essay using your rubric
- Outputs scores + justifications + feedback

### Layer 2: Judge Model (Evaluator)
- GPT-4o (specified in [evals/essay-grading.yaml](evals/essay-grading.yaml))
- Evaluates if the grading was reasonable
- Checks if justifications match scores
- Verifies feedback is constructive and actionable

## Key Metrics

| Metric | What It Measures | How It's Calculated |
|--------|------------------|---------------------|
| **Agreement with humans** | Model score vs human score | ±1 point tolerance |
| **Trait-level accuracy** | Per-dimension scores | 4 separate checks for Content, Organization, Word Choice, Conventions |
| **Reasoning quality** | Justification → score connection | LLM judge with rubric |
| **Format compliance** | All sections present | JavaScript assertion |

## Next Steps

### 1. Run Initial Evaluation
```bash
npx promptfoo eval
npx promptfoo view
```

### 2. Review Results
- Which model matches human scores best?
- Which provides better reasoning/feedback?
- Are there systematic biases?

### 3. Iterate on the Grading Prompt
The grading prompt in [prompts/essay_grader.txt](prompts/essay_grader.txt) is where you'll likely spend most optimization time.

Try adjusting:
- How specific the scoring criteria are
- Whether to include example scores
- The format of the output
- Emphasis on different rubric dimensions

### 4. Calibrate the Judge
Before scaling up, validate the LLM judge:
1. Run on 10-15 essays
2. Manually check if judge's pass/fail matches your intuition
3. Adjust the `llm-rubric` criteria in [evals/essay-grading.yaml](evals/essay-grading.yaml#L41-L46) if needed

### 5. Scale to Real Data
When ready, follow the [ASAP-dataset-guide.md](ASAP-dataset-guide.md) to:
- Download ASAP or ASAP++ dataset
- Convert to YAML format
- Test on 20-30 essays, then scale to hundreds

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│ promptfooconfig.yaml                                    │
│ • 3 providers (GPT-4o-mini, GPT-4o, Claude)            │
│ • References prompts, tests, evals                      │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Prompts      │  │ Test Inputs  │  │ Evaluations  │
│              │  │              │  │              │
│ essay_grader │  │ essays.yaml  │  │ essay-grading│
│ .txt         │  │ (5 samples)  │  │ .yaml        │
│              │  │              │  │ (7 assertions│
│ Defines how  │  │ Real essays  │  │              │
│ to grade     │  │ + human      │  │ Checks score │
│              │  │ scores       │  │ accuracy +   │
│              │  │              │  │ reasoning    │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Example Output

When you run the evaluation, each model will produce output like:

```
Content: 5 - The essay effectively addresses the prompt with a clear
personal narrative about teaching patience. Specific details like
"two whole weeks of practice" and "small blue bicycle" bring the
story to life.

Organization: 5 - Clear introduction establishes the topic, body
paragraphs develop the narrative chronologically, and conclusion
reflects on the broader lesson learned. Smooth transitions between
paragraphs.

Word Choice: 4 - Generally appropriate and varied vocabulary. Phrases
like "staying calm and supportive" are precise. Could use more
sophisticated word choices in places.

Conventions: 5 - Consistently correct spelling, grammar, and
punctuation throughout. Sentence structure is varied and appropriate.

Overall Score: 5

Feedback: This is a strong narrative essay that effectively illustrates
the importance of patience through a relatable personal experience.
Your use of specific details makes the story engaging. To improve,
consider using more varied and sophisticated vocabulary, and perhaps
explore the emotional complexity of the experience more deeply.
```

The evaluations will then check:
- ✓ Overall score 5 matches human score 5
- ✓ Content score 5 matches human score 5
- ✓ Organization score 5 matches human score 5
- ✓ Word choice score 4 matches human score 4 (within ±1)
- ✓ Conventions score 5 matches human score 5
- ✓ Reasoning quality is good (LLM judge)
- ✓ All required sections present

## Troubleshooting

### Issue: Models not matching human scores

**Solution:** This is expected! The goal is to compare models to see which one matches humans best. If all models are consistently off, you might need to:
1. Adjust the rubric to be more specific
2. Provide scoring examples in the prompt
3. Check if score scales are aligned (some ASAP sets use different ranges)

### Issue: LLM judge being too harsh/lenient

**Solution:** Edit the `llm-rubric` criteria in [evals/essay-grading.yaml](evals/essay-grading.yaml#L41-L46) to adjust what "good reasoning" means.

### Issue: Format errors

**Solution:** Models might format responses differently. Check the regex patterns in [evals/essay-grading.yaml](evals/essay-grading.yaml) and adjust if needed.

## Resources

- **Promptfoo Docs**: https://www.promptfoo.dev/docs/
- **LLM-as-Judge Guide**: https://www.promptfoo.dev/docs/guides/llm-as-judge/
- **ASAP Dataset**: https://www.kaggle.com/c/asap-aes
- **ASAP++ Dataset**: https://lwsam.github.io/ASAP++/

---

**Ready to start?** Run `npx promptfoo eval` and then `npx promptfoo view` to see your results!
