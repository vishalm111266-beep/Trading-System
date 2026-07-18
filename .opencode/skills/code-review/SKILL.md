---
name: code-review
description: Structured code review checklist and patterns. Use when user says "review code", "check quality", "audit", or "review this PR".
---

# Code Review Skill

Structured approach to reviewing code for correctness, quality, and security.

## Review Checklist

### 1. Correctness
- [ ] Does the code do what the PR/issue claims?
- [ ] Are edge cases handled?
- [ ] Could this break existing functionality?
- [ ] Are error cases properly handled?

### 2. Security
- [ ] Any injection vulnerabilities (SQL, XSS, command)?
- [ ] Proper input validation?
- [ ] No secrets or credentials exposed?
- [ ] Proper authentication/authorization?

### 3. Performance
- [ ] Any obvious O(n²) or worse patterns?
- [ ] Memory leaks possible?
- [ ] Unnecessary recomputation?
- [ ] Database queries in loops?

### 4. Maintainability
- [ ] Code follows project style/conventions?
- [ ] Appropriate comments?
- [ ] Functions reasonably sized (under 50 lines)?
- [ ] Clear variable/function names?

### 5. Testing
- [ ] Are there tests for new functionality?
- [ ] Do tests cover edge cases?
- [ ] Are tests isolated properly?

## Review Severity

| Severity | Description | Action Required |
|----------|-------------|-----------------|
| Critical | Security vulnerability or data loss possible | Must fix before merge |
| Major | Bug or significant design issue | Should fix before merge |
| Minor | Style, naming, or small improvement | Nice to fix |
| Suggestion | Ideals, not problems | Consider for future |

## Output Format

```
## Review Summary
[1-2 sentence overall assessment]

## Issues Found

### [CRITICAL] Issue Title
Location: `file:line`
Description: What's wrong
Fix: How to fix it

### [MAJOR] Issue Title
...

## Recommendations
1. ...
2. ...

## Approved: YES/NO
Reason: ...
```