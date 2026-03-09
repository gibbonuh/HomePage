#!/bin/zsh
set -euo pipefail

ROOT="/Users/emmett/Documents/New project 3"
BUILD_SCRIPT="$ROOT/scripts/build_batch.py"
START_BATCH="${1:-7}"
BATCH_SIZE="${2:-10}"
MAX_GAME_MB="${3:-45}"

if [[ ! -f "$BUILD_SCRIPT" ]]; then
  echo "Missing script: $BUILD_SCRIPT"
  exit 1
fi

cd "$ROOT"

for ((n=START_BATCH; n<1000; n++)); do
  echo ""
  echo "=== Building batch $n ==="
  OUTPUT="$(python3 "$BUILD_SCRIPT" --label "$n" --batch-size "$BATCH_SIZE" --max-game-mb "$MAX_GAME_MB")"
  echo "$OUTPUT"

  if echo "$OUTPUT" | rg -q "No eligible games left"; then
    echo "No more eligible games to add. Done."
    break
  fi

  git add extra-games.json games
  if git diff --cached --quiet; then
    echo "No staged changes for batch $n. Stopping."
    break
  fi

  git commit -m "Add batch $n games"
  git push origin main
done
