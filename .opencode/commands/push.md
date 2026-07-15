---
description: Push files to GitHub with LFS handling and cleanup
agent: general
---

Push to GitHub: $ARGUMENTS

1. @github-pusher — handle LFS configuration, large file detection, push, and cleanup

Steps:
- Check LFS status and .gitattributes
- Detect any files >100MB not tracked by LFS
- Configure LFS tracking if needed
- Commit with proper sequence (.gitattributes first)
- Push to GitHub
- Verify LFS upload succeeded
- Clean local data files to free phone storage
- Report results
