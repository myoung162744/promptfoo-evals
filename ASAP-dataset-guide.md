# ASAP Dataset Integration Guide

This guide explains how to download and integrate the real ASAP (Automated Student Assessment Prize) dataset into your essay grading evaluation.

## Current Setup

Your evaluation is currently set up with **5 sample essays** that mimic the ASAP dataset format. These are in [test-inputs/essays.yaml](test-inputs/essays.yaml) and are ready to use for testing your setup.

## Getting the Real ASAP Dataset

### Option 1: ASAP Dataset (Basic)

The original ASAP dataset contains ~13,000 essays with holistic scores.

**Download:**
```bash
# Install Kaggle CLI
pip install kaggle

# Download dataset (requires Kaggle account and API key)
kaggle competitions download -c asap-aes

# Unzip
unzip asap-aes.zip
```

**What you get:**
- 8 essay sets, each from a different prompt
- Grades 7-10
- 1,700+ essays per topic (except one with ~500)
- Each essay has a holistic score (1-6 or similar scale)

### Option 2: ASAP++ Dataset (Recommended)

The ASAP++ dataset includes **trait-specific scores** (Content, Organization, Word Choice, etc.) which matches the rubric structure in your evaluation.

**Download:**
- Visit: https://lwsam.github.io/ASAP++/lrec2018.html
- Download the ASAP++ dataset
- Follow their instructions for accessing the data

**What you get:**
- All essays from ASAP dataset
- **Attribute-specific scores**: Content, Organization, Word Choice, Sentence Fluency, Conventions
- Better alignment with multi-dimensional rubrics

## Converting ASAP Data to Your Format

The ASAP dataset comes as CSV/TSV files. You'll need to convert them to YAML format for Promptfoo.

### Sample Python Script

```python
import pandas as pd
import yaml

# Load ASAP data
df = pd.read_csv('training_set_rel3.tsv', sep='\t', encoding='latin-1')

# Filter to one essay set (e.g., set 1)
essay_set = df[df['essay_set'] == 1]

# Convert to Promptfoo format
test_cases = []
for idx, row in essay_set.head(20).iterrows():  # Start with 20 essays
    test_case = {
        'description': f"Essay {row['essay_id']} - Score {row['domain1_score']}",
        'vars': {
            'essay_prompt': "Write about a time when patience was important to you.",  # Add actual prompt
            'rubric': """
Content (1-6): Does the essay address the prompt with relevant details?
Organization (1-6): Is there a clear introduction, body, and conclusion?
Word Choice (1-6): Are words precise and appropriate?
Conventions (1-6): Are spelling, grammar, and punctuation correct?
            """.strip(),
            'essay': row['essay'],
            'human_score': int(row['domain1_score']),
            # If using ASAP++, add trait scores:
            # 'human_content_score': int(row['content_score']),
            # 'human_organization_score': int(row['organization_score']),
            # etc.
        }
    }
    test_cases.append(test_case)

# Save to YAML
with open('test-inputs/essays-asap.yaml', 'w') as f:
    yaml.dump(test_cases, f, default_flow_style=False, allow_unicode=True)
```

### For ASAP++ with Trait Scores

If you're using ASAP++, update the script to include all trait scores:

```python
'human_score': int(row['domain1_score']),
'human_content_score': int(row['content']),
'human_organization_score': int(row['organization']),
'human_word_choice_score': int(row['word_choice']),
'human_conventions_score': int(row['conventions']),
```

## Integration Steps

### 1. Start Small
Begin with 20-30 essays from one essay set to validate your setup:

```bash
# Run evaluation with sample data first
npx promptfoo eval

# View results
npx promptfoo view
```

### 2. Calibrate Your Judge
Before trusting the `llm-rubric` assertions, manually review outputs:

1. Run evaluation on 10-15 essays
2. Check if the LLM judge's pass/fail matches your own judgment
3. Adjust the `llm-rubric` criteria in [evals/essay-grading.yaml](evals/essay-grading.yaml) if needed

### 3. Scale Up
Once calibrated, expand to more essays:

```yaml
# In promptfooconfig.yaml, you can create separate test files
tests:
  - file://test-inputs/essays.yaml          # Sample essays (5)
  - file://test-inputs/essays-asap-set1.yaml # ASAP Set 1 (50 essays)
  - file://test-inputs/essays-asap-set2.yaml # ASAP Set 2 (50 essays)
```

## Understanding Essay Sets

The ASAP dataset has 8 different essay sets, each with different prompts and rubrics:

| Set | Type | Prompt Topic | Score Range |
|-----|------|--------------|-------------|
| 1 | Persuasive | More to it than fun and games | 2-12 |
| 2 | Persuasive | Censorship in libraries | 1-6 |
| 3 | Source-dependent | Patience and Butterfly | 0-3 |
| 4 | Source-dependent | Winter Hibiscus | 0-3 |
| 5 | Source-dependent | Dangerous Situations | 0-4 |
| 6 | Source-dependent | The Mooring Mast | 0-4 |
| 7 | Narrative | Laughter or Patience | 0-30 |
| 8 | Narrative | Describe a person you admire | 0-60 |

**Note:** Different sets have different scoring scales. You'll need to normalize these or adjust your rubric scoring to match.

## What Success Looks Like

Your evaluation measures four key metrics:

1. **Score Accuracy**: Model's overall score vs. human score (±1 tolerance)
2. **Trait-Level Accuracy**: Per-dimension scores (Content, Organization, etc.)
3. **Reasoning Quality**: LLM judge evaluates if justifications match scores
4. **Format Compliance**: Ensures all required sections are present

### Interpreting Results

In the Promptfoo UI, you'll see:

- **Pass Rate**: Percentage of assertions that passed
- **Score**: Weighted average (0-1) across all assertions
- **Comparison**: Side-by-side view of GPT-4o vs Claude vs GPT-4o-mini

Look for:
- Which model best matches human scores?
- Which model provides better reasoning/feedback?
- Are there systematic biases (e.g., always scoring 1 point higher)?

## Tips for Success

1. **Start with one essay set** - Each has different prompts/rubrics
2. **Normalize scores** - Convert all to 1-6 scale for consistency
3. **Include the actual prompt** - Essential for source-dependent responses
4. **Balance your test set** - Include high, medium, and low scoring essays
5. **Iterate on your grading prompt** - This is where you'll spend most time optimizing

## Next Steps

1. Run the current evaluation with sample data:
   ```bash
   npx promptfoo eval
   npx promptfoo view
   ```

2. Review results and iterate on [prompts/essay_grader.txt](prompts/essay_grader.txt)

3. Download ASAP/ASAP++ data when ready to scale

4. Create conversion script to generate more test cases

5. Compare model performance and choose the best grader

## Questions?

- Check Promptfoo docs: https://www.promptfoo.dev/docs/
- ASAP dataset info: https://www.kaggle.com/c/asap-aes
- ASAP++ dataset: https://lwsam.github.io/ASAP++/
