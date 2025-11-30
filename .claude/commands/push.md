---
description: Push changes to GitHub with auto-generated commit message
---

You are helping push changes to GitHub. Follow these steps:

1. Run `git status` to see what files have changed
2. Run `git diff` to see the actual changes (limit to key files if many changes)
3. Analyze the changes and create a clear, descriptive commit message that:
   - Has a concise subject line (50 chars or less)
   - Explains what changed and why
   - Uses imperative mood ("Add feature" not "Added feature")
   - Includes bullet points for multiple changes
4. Stage all changes with `git add -A`
5. Commit with the auto-generated message including the Claude Code footer:
   ```
   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```
6. Push to the current branch with `git push`
7. Show the commit hash and confirmation

IMPORTANT:
- Do not ask for confirmation, just analyze and push
- Be concise in your commit messages
- Focus on the "what" and "why" of changes
