#!/bin/bash
# Smart Push - Push to GitHub then clean local data
# Saves phone memory by keeping data only on GitHub
# Usage: bash scripts/smart-push.sh "commit message"

set -e

PROJECT_DIR="$HOME/Projects/Trading-System"
cd "$PROJECT_DIR"

MSG="${1:-chore: push data and clean local}"

echo "=== Smart Push: GitHub + Phone Cleanup ==="
echo ""

# 1. Add all changes
echo "[1/4] Staging changes..."
git add -A

# 2. Commit
echo "[2/4] Committing..."
git commit -m "$MSG" 2>/dev/null || echo "  Nothing to commit"

# 3. Push to GitHub (including LFS files)
echo "[3/4] Pushing to GitHub (including LFS files)..."
git push origin main 2>&1 || echo "  Push failed - check connection"

# 4. Clean local data (keep code, remove data files)
echo "[4/4] Cleaning local data to save phone memory..."
find "$PROJECT_DIR/data" -name "*.csv" -delete 2>/dev/null || true
find "$PROJECT_DIR/data" -name "*.parquet" -delete 2>/dev/null || true
find "$PROJECT_DIR/data" -name "*.db" -delete 2>/dev/null || true
find "$PROJECT_DIR/data" -name "*.sqlite" -delete 2>/dev/null || true
rm -rf "$PROJECT_DIR/data/cache" 2>/dev/null || true
rm -rf "$PROJECT_DIR/reports/"*.html "$PROJECT_DIR/reports/"*.pdf 2>/dev/null || true

echo ""
echo "=== Done ==="
echo "Code + data pushed to GitHub"
echo "Local data cleaned to save phone storage"
echo ""
echo "To get data back later:"
echo "  git lfs pull"
