#!/usr/bin/env bash
# Symlink the harness into ~/.claude. Dry run by default; pass --apply to make links.
# Never overwrites an existing file that is not already a symlink. settings.json is not touched.
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"
DEST="${CLAUDE_HOME:-$HOME/.claude}"
APPLY=0; [ "${1:-}" = "--apply" ] && APPLY=1

link() { # src dst
  if [ -e "$2" ] && [ ! -L "$2" ]; then echo "skip   $2 (exists, not a symlink)"; return; fi
  # if ~/.claude/skills etc. is itself a symlink to another folder (e.g. a synced one), linking into it would change that folder
  if [ -L "$(dirname "$2")" ]; then echo "skip   $2 (parent $(dirname "$2") is a symlink -> $(readlink "$(dirname "$2")"); link manually)"; return; fi
  if [ $APPLY -eq 1 ]; then mkdir -p "$(dirname "$2")"; ln -sfn "$1" "$2"; echo "linked $2"; else echo "would  $2 -> $1"; fi
}

link "$REPO/docs/llm-tutor-system.md" "$DEST/llm-tutor-system.md"
for s in "$REPO"/skills/*/; do link "${s%/}" "$DEST/skills/$(basename "$s")"; done
for c in "$REPO"/commands/*.md; do link "$c" "$DEST/commands/$(basename "$c")"; done
link "$REPO/hooks/coverage_judge_gate.sh" "$DEST/hooks/coverage_judge_gate.sh"

cat <<EOF

Next (manual):
  1. Merge settings.example.json into $DEST/settings.json and set STUDY_ROOT.
  2. Copy templates/study-root-CLAUDE.md to \$STUDY_ROOT/CLAUDE.md and one
     templates/course-CLAUDE.md per course folder.
  3. For PDF conversion: cp scripts/.env.example scripts/.env and add Mathpix keys.
EOF
[ $APPLY -eq 1 ] || echo "(dry run — rerun with --apply)"
