#!/bin/bash

# Essay Grading Evaluation - Quick Start Script
# This script helps you run the essay grading evaluation

set -e

echo "=========================================="
echo "Essay Grading Evaluation Setup"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: No .env file found"
    echo "Make sure you have API keys set up for:"
    echo "  - OPENAI_API_KEY (for GPT-4o and GPT-4o-mini)"
    echo "  - ANTHROPIC_API_KEY (for Claude Sonnet 4)"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📋 Current setup:"
echo "  • Prompt: prompts/essay_grader.txt"
echo "  • Test cases: test-inputs/essays.yaml (5 sample essays)"
echo "  • Evaluations: evals/essay-grading.yaml (7 assertions)"
echo "  • Models: GPT-4o-mini, GPT-4o, Claude Sonnet 4"
echo ""

# Check if user wants to run specific test
echo "What would you like to do?"
echo "  1) Run full evaluation (all 3 models on all 5 essays)"
echo "  2) Run with just GPT-4o-mini (faster, cheaper)"
echo "  3) View existing results"
echo "  4) Cancel"
echo ""
read -p "Choose (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Running full evaluation..."
        echo "This will test 3 models × 5 essays = 15 test cases"
        echo ""
        npx promptfoo eval
        echo ""
        echo "✅ Evaluation complete!"
        echo ""
        read -p "Open results viewer? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            npx promptfoo view
        fi
        ;;
    2)
        echo ""
        echo "🚀 Running evaluation with GPT-4o-mini only..."
        echo ""
        npx promptfoo eval -p "openai:gpt-4o-mini"
        echo ""
        echo "✅ Evaluation complete!"
        echo ""
        read -p "Open results viewer? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            npx promptfoo view
        fi
        ;;
    3)
        echo ""
        echo "📊 Opening results viewer..."
        npx promptfoo view
        ;;
    4)
        echo ""
        echo "Cancelled."
        exit 0
        ;;
    *)
        echo ""
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Next steps:"
echo "  • Review results in the web UI"
echo "  • Compare which model grades most like humans"
echo "  • Iterate on prompts/essay_grader.txt if needed"
echo "  • See ASAP-dataset-guide.md to scale up to real data"
echo "=========================================="
