---
name: github-pusher
description: Push large files to GitHub with Git LFS handling. Use when user says "push to github", "push data", "upload files", "push large files", or when git push fails with file size errors.
---

# GitHub Push Skill

## Trigger Words
- "push to github"
- "push data"
- "upload files"
- "push large files"
- "git push failed"
- "file too large"

## Pipeline
1. @github-pusher → handle LFS, push, cleanup

## Key Rules
1. .gitattributes MUST be committed before large files
2. Files >100MB MUST go through LFS
3. ALWAYS verify push before deleting local data
4. ALWAYS clean local data after push (phone storage)

## Common Errors
- "exceeds GitHub's file size limit of 100 MB" → Add to LFS tracking
- "pack exceeds maximum allowed size" → Split push into chunks
- LFS upload failed → Run `git lfs push --all origin`

## Post-Push Cleanup
```bash
find . -name "*.csv" -not -path "./.git/*" -delete
find . -name "*.parquet" -not -path "./.git/*" -delete
find . -name "*.db" -not -path "./.git/*" -delete
git lfs prune
```
