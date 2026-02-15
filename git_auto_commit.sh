#!/bin/bash

# Auto-commit and push helper script
# Usage: ./git_auto_commit.sh "your commit message"

cd "$(dirname "$0")"

# Get commit message from argument or use default
COMMIT_MSG="${1:-Automated update from Claude Code}"

# Check if there are changes
if ! git diff-index --quiet HEAD --; then
    echo "📝 Committing changes..."
    git add -A
    git commit -m "$(cat <<EOF
$COMMIT_MSG

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
EOF
)"

    # Push to GitHub
    echo "🚀 Pushing to GitHub..."
    git push origin main

    # Show status
    echo "✅ Commit and push complete!"
    git log -1 --oneline
else
    echo "⚠️  No changes to commit"
fi
