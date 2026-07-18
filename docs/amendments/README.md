# Amendments

This directory contains architecture amendments. Each amendment must be approved before merging.

## Naming Convention

`00X-YYYY-MM-DD-brief-description.md`

## Amendment Process

1. Create amendment file with proposed change
2. Invoke @architect to review
3. Invoke @reviewer for approval
4. Await explicit user approval
5. Merge only after all three steps complete

## Amendment Template

```markdown
# Amendment: [Brief Title]

**Date:** YYYY-MM-DD
**Author:** [who proposed]
**Status:** PROPOSED | APPROVED | REJECTED

## Change

[What is changing]

## Rationale

[Why this change is needed]

## Impact

[What this affects]
```