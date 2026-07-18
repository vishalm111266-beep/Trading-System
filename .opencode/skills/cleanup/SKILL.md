---
name: cleanup
description: Clean up workspace, stale experiment folders, or generated artifacts. Use when user says "clean up", "cleanup workspace", or "remove old experiments".
---

# Cleanup Skill

## When to use

Use when user wants to remove transient files, stale experiments, or workspace artifacts.

## Cleanup Scopes

### Workspace (generated artifacts)
```bash
workspace/          # plots, reports, exports
```
These are never git-tracked and can always be deleted.

### Research Experiments
```bash
research/exp-XXX-name/   # individual experiment folders
```
Delete only with explicit user approval.

### Data Cache
```bash
data/cache/         # cached market data
data/storage/       # stored datasets
```
Clean with `scripts/phone-cleanup.sh` — do not manually delete.

### Git LFS Tracking
If files were added to LFS but are no longer needed:
```bash
git lfs untrack "*.csv"
git rm --cached data.csv
```

## Rules

1. **Never delete `core/`**, `strategies/`, `docs/`, `config/`, `scripts/`, or `.opencode/`
2. **Never delete experiment folders** without explicit user approval
3. **Never delete `tests/`**
4. Always show `git status` before and after cleanup
5. After any deletion that affects git, run `git status` and confirm
6. If deleting large files, verify they are not in the git history before force-removing

## Standard Cleanup Workflow

```bash
# 1. Show what would be affected
git status

# 2. Remove workspace artifacts (safe)
rm -rf workspace/*

# 3. If removing experiment folder:
#    - Confirm with user first
#    - Remove folder
#    - git add -A && git commit -m "chore: remove exp-XXX"

# 4. Verify
git status
```

## Emergency Recovery

If cleanup deleted something important, use:
```bash
git checkout HEAD -- <file>
git log --oneline -5  # find recent commits
```