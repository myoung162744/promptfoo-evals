#!/bin/bash

# Quick Git Push Script
# Usage: ./push.sh [optional commit message]

set -e

# Check if there are changes
if [[ -z $(git status -s) ]]; then
    echo "No changes to commit."
    exit 0
fi

echo "📋 Changes detected:"
git status -s
echo ""

# Use provided message or generate a simple one
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
else
    # Auto-generate based on changed files
    CHANGED_FILES=$(git status -s | wc -l | xargs)
    COMMIT_MSG="Update $CHANGED_FILES file(s)"
fi

# Add footer
FULL_MSG="$COMMIT_MSG

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "📝 Commit message: $COMMIT_MSG"
echo ""

# Stage, commit, push
git add -A
git commit -m "$FULL_MSG"
git push

echo ""
echo "✅ Pushed successfully!"
git log -1 --oneline
