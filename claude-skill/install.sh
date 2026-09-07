#!/usr/bin/env bash
# Install the self-contained `pravachan` superskill into Claude Code.
# Usage: ./install.sh [--project]   (default: global ~/.claude/skills)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ "${1:-}" == "--project" ]]; then DEST="$(pwd)/.claude/skills"; else DEST="$HOME/.claude/skills"; fi
mkdir -p "$DEST"
cp -R "$HERE/pravachan" "$DEST/"
echo "installed → $DEST/pravachan"
echo "run bootstrap once:  python3 \"$DEST/pravachan/scripts/bootstrap.py\""
echo "then in Claude Code:  /pravachan   (or just paste a YouTube/Drive link or audio path)"
