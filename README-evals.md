# Promptfoo Evaluation Framework

A modular, scalable structure for creating and managing prompt evaluations with reusable components.

## 📁 Project Structure

```
promptfoo-evals/
├── promptfooconfig.yaml          # Main configuration file
├── prompts/                       # Prompt templates (one per use case)
│   ├── translation.txt
│   └── summarization.txt
├── test-inputs/                   # Test scenarios (one-to-many per use case)
│   ├── translation.yaml
│   └── summarization.yaml
├── evals/                         # Reusable evaluation assertions
│   ├── translation-quality.yaml   # Translation-specific evals
│   ├── language-checks.yaml       # Generic language quality checks
│   └── llm-judge.yaml             # LLM-as-judge evaluations
└── README-evals.md                # This file
```

## 🚀 Quick Start

### Running Evaluations

```bash
# Run all evaluations
npx promptfoo@latest eval

# Run with web UI
npx promptfoo@latest view

# Run specific use case (if configured separately)
npx promptfoo@latest eval -c promptfooconfig.yaml
```

### Prerequisites

1. Install Node.js (v16 or later)
2. Set up API keys as environment variables:
   ```bash
   export OPENAI_API_KEY=your-key-here
   # or
   export ANTHROPIC_API_KEY=your-key-here
   ```

## 📝 Adding a New Use Case

Follow these 4 steps to add a new use case:

### Step 1: Create a Prompt Template

Create a new file in `prompts/` directory:

**Example:** `prompts/sentiment-analysis.txt`
```
Analyze the sentiment of the following text and classify it as positive, negative, or neutral:

{{inputText}}

Provide your classification and a brief explanation.
```

### Step 2: Create Test Input Cases

Create a new file in `test-inputs/` directory with multiple test scenarios:

**Example:** `test-inputs/sentiment-analysis.yaml`
```yaml
# Sentiment Analysis Test Cases

- description: "Positive review"
  vars:
    inputText: "This product is amazing! I absolutely love it."

- description: "Negative review"
  vars:
    inputText: "Terrible experience. Would not recommend."

- description: "Neutral statement"
  vars:
    inputText: "The product arrived on time and works as expected."
```

### Step 3: Reference in Main Config

Add a new section to `promptfooconfig.yaml`:

```yaml
- description: "Sentiment Analysis Use Case"
  prompts:
    - file://prompts/sentiment-analysis.txt
  
  tests:
    - file://test-inputs/sentiment-analysis.yaml
  
  defaultTest:
    assert:
      # Reuse existing evals
      - file://evals/language-checks.yaml
      - file://evals/llm-judge.yaml
      # Add custom assertions if needed
      - type: contains-any
        value: ["positive", "negative", "neutral"]
        description: "Output should contain sentiment classification"
```

### Step 4: (Optional) Create Custom Evals

If you need use-case-specific evaluations, create a new file in `evals/`:

**Example:** `evals/sentiment-checks.yaml`
```yaml
- type: contains-any
  value: ["positive", "negative", "neutral"]
  description: "Output should classify sentiment"

- type: javascript
  value: |
    // Check that output contains an explanation
    return output.length > 20;
  description: "Output should include explanation"
```

Then reference it in your use case config:
```yaml
assert:
  - file://evals/sentiment-checks.yaml
  - file://evals/language-checks.yaml
```

## 🔧 Understanding the Structure

### Prompts (`prompts/`)

- **One file per use case**
- Contains prompt template with variable placeholders: `{{variableName}}`
- Variables are injected from test input files
- Keep prompts focused and single-purpose

### Test Inputs (`test-inputs/`)

- **One file per use case, multiple test cases per file**
- YAML format with array of test scenarios
- Each test defines:
  - `description`: What the test is checking
  - `vars`: Variables to inject into the prompt template
- Aim for 5-10 test cases to cover different scenarios

### Evals (`evals/`)

- **Grouped assertions by functionality**
- Each file contains multiple related evaluation checks
- Can be reused across multiple use cases
- Common eval types:
  - `contains` / `not-contains`: Check for specific text
  - `javascript`: Custom logic with code
  - `model-graded-closedqa`: LLM judges yes/no questions
  - `llm-rubric`: LLM judges with detailed scoring criteria
  - `cost`: Check cost thresholds

## 📊 Example Use Cases

### Translation

**Prompt:** `prompts/translation.txt`
- Translates text between languages
- Variables: `inputLanguage`, `outputLanguage`, `inputText`

**Test Inputs:** `test-inputs/translation.yaml`
- 7 test cases covering different language pairs and text types

**Evals:**
- `translation-quality.yaml` - Translation-specific checks
- `language-checks.yaml` - Generic quality checks (shared)
- `llm-judge.yaml` - Semantic quality checks (shared)

### Summarization

**Prompt:** `prompts/summarization.txt`
- Summarizes text with configurable length and tone
- Variables: `summaryLength`, `tone`, `inputText`

**Test Inputs:** `test-inputs/summarization.yaml`
- 5 test cases covering different content types and summary styles

**Evals:**
- `language-checks.yaml` - Generic quality checks (reused)
- `llm-judge.yaml` - Semantic quality checks (reused)
- Custom inline assertion for length check

## 🎯 Best Practices

### 1. **Reuse Evals Across Use Cases**
   - Create generic eval files like `language-checks.yaml`
   - Reference them in multiple use cases
   - Update once, apply everywhere

### 2. **Keep Prompts Focused**
   - One prompt per specific task
   - Use clear variable names
   - Document expected variable types

### 3. **Comprehensive Test Coverage**
   - Test edge cases and common scenarios
   - Include both positive and negative cases
   - Add descriptive names to each test

### 4. **Mix Eval Types**
   - Combine simple checks (contains, length) with semantic checks (LLM judge)
   - Use cost checks to prevent expensive runs
   - Use JavaScript for custom logic

### 5. **Organize by Functionality**
   - Group related evals in the same file
   - Name files clearly (`translation-quality.yaml`, not `evals1.yaml`)
   - Keep use-case-specific evals separate from shared ones

## 🔍 Common Eval Patterns

### Basic Output Quality
```yaml
- type: javascript
  value: "output.length > 0"
  description: "Output should not be empty"
```

### Specific Content Check
```yaml
- type: contains
  value: "expected phrase"
  description: "Output should contain expected phrase"
```

### LLM-as-Judge
```yaml
- type: model-graded-closedqa
  value: "Is the output accurate and relevant?"
  threshold: 0.8
  description: "Quality check using LLM judge"
```

### Custom JavaScript Logic
```yaml
- type: javascript
  value: |
    // Access output and context
    const wordCount = output.split(' ').length;
    const inputWordCount = context.vars.inputText.split(' ').length;
    return wordCount < inputWordCount;
  description: "Custom logic with full context"
```

### Cost Control
```yaml
- type: cost
  threshold: 0.01
  description: "Keep costs under control"
```

## 🛠️ Advanced Features

### Multiple Prompts per Use Case

You can test multiple prompt variations:

```yaml
- description: "A/B Test Use Case"
  prompts:
    - file://prompts/version-a.txt
    - file://prompts/version-b.txt
  tests:
    - file://test-inputs/common-tests.yaml
```

### Provider-Specific Configuration

Test different models for different use cases:

```yaml
- description: "Translation Use Case"
  prompts:
    - file://prompts/translation.txt
  providers:
    - openai:gpt-4  # Override default provider
  tests:
    - file://test-inputs/translation.yaml
```

### Test-Specific Overrides

Override variables or add test-specific assertions:

```yaml
tests:
  - file://test-inputs/translation.yaml
  - vars:
      inputLanguage: English
      outputLanguage: Klingon
    assert:
      - type: contains
        value: "tlhIngan"
        description: "Should attempt Klingon translation"
```

## 📚 Resources

- [Promptfoo Documentation](https://www.promptfoo.dev/docs/intro)
- [Assertion Types](https://www.promptfoo.dev/docs/configuration/expected-outputs)
- [LLM-as-Judge](https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded)
- [JavaScript Assertions](https://www.promptfoo.dev/docs/configuration/expected-outputs/javascript)

## 🤝 Contributing

When adding new use cases or evals to this repository:

1. Follow the naming conventions
2. Add descriptive comments
3. Update this README with your use case
4. Test your configuration before committing

## 📄 License

[Your License Here]
