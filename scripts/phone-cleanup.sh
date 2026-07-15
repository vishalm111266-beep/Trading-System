#!/bin/bash
# Phone Storage Cleanup Script for Trading System
# Run this regularly to keep phone memory free
# Usage: bash scripts/phone-cleanup.sh

set -e

PROJECT_DIR="$HOME/Projects/Trading-System"
FREED=0

echo "=== Trading System Phone Cleanup ==="
echo ""

# 1. Clean Python caches
echo "[1/7] Cleaning Python caches..."
CLEANED=$(find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && echo "done" || echo "none")
find "$PROJECT_DIR" -name "*.pyc" -delete 2>/dev/null || true
echo "  Python caches cleaned"

# 2. Clean pytest cache
echo "[2/7] Cleaning pytest cache..."
rm -rf "$PROJECT_DIR/.pytest_cache" 2>/dev/null || true
find "$PROJECT_DIR" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
echo "  Pytest cache cleaned"

# 3. Clean .venv if not needed (saves ~31MB)
echo "[3/7] Checking .venv size..."
VENV_SIZE=$(du -sm "$PROJECT_DIR/.venv" 2>/dev/null | cut -f1 || echo "0")
echo "  .venv size: ${VENV_SIZE}MB"
if [ "$1" = "--deep" ]; then
    echo "  Removing .venv (deep clean)..."
    rm -rf "$PROJECT_DIR/.venv"
    echo "  .venv removed (saved ${VENV_SIZE}MB)"
    FREED=$((FREED + VENV_SIZE))
else
    echo "  Skipping .venv (use --deep to remove)"
fi

# 4. Clean data cache
echo "[4/7] Cleaning data cache..."
CACHE_SIZE=$(du -sm "$PROJECT_DIR/data/cache" 2>/dev/null | cut -f1 || echo "0")
rm -rf "$PROJECT_DIR/data/cache" 2>/dev/null || true
echo "  Cache cleaned (saved ${CACHE_SIZE}MB)"
FREED=$((FREED + CACHE_SIZE))

# 5. Clean old reports
echo "[5/7] Cleaning old reports..."
REPORT_SIZE=$(du -sm "$PROJECT_DIR/reports" 2>/dev/null | cut -f1 || echo "0")
rm -f "$PROJECT_DIR/reports/"*.html "$PROJECT_DIR/reports/"*.pdf "$PROJECT_DIR/reports/"*.csv 2>/dev/null || true
echo "  Reports cleaned (saved ${REPORT_SIZE}MB)"
FREED=$((FREED + REPORT_SIZE))

# 6. Clean Termux cache
echo "[6/7] Cleaning Termux package cache..."
apt-get clean 2>/dev/null || true
apt-get autoremove -y 2>/dev/null || true
echo "  Termux cache cleaned"

# 7. Clear proot distro cache if exists
echo "[7/7] Clearing proot distro cache..."
proot-distro clear-cache 2>/dev/null || echo "  No proot cache to clear"

echo ""
echo "=== Cleanup Complete ==="
echo "Freed approximately ${FREED}MB from phone storage"
echo ""

# Show current disk usage
echo "Current storage:"
df -h / | tail -1 | awk '{print "  Used: "$3" / Total: "$2" ("$5" used)"}'
echo ""

# Git LFS status
echo "Git LFS status:"
cd "$PROJECT_DIR"
git lfs ls-files 2>/dev/null | head -10 || echo "  No LFS files tracked"
echo ""
echo "Tip: Use 'git lfs pull' to download data files from GitHub when needed"
echo "Tip: Use 'bash scripts/phone-cleanup.sh --deep' to also remove .venv"
