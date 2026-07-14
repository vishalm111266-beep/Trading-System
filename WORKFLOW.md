# WORKFLOW.md

Development and research workflow for the Trading System.

## Daily Workflow

### Research Phase
1. Define research question in `research/active/`
2. Gather data into `data/`
3. Document findings in `research/findings/`
4. Archive completed research in `research/archive/`

### Development Phase
1. Check `ROADMAP.md` for current priorities
2. Create or modify code in the appropriate module
3. Write tests in `tests/`
4. Run verification suite
5. Update `CHANGELOG.md` if significant

### Review Phase
1. Review changes against `FOUNDATION.md` principles
2. Verify no strategy logic was introduced
3. Check error handling and edge cases
4. Confirm documentation is current

## Directory Conventions

### Adding a New Indicator (Python)
```
python/indicators/<name>.py     # Implementation
tests/unit/test_<name>.py       # Tests
python/indicators/__init__.py   # Export
```

### Adding a New Indicator (Pine Script)
```
pine/indicators/<name>.pine     # Implementation
pine/libraries/                  # Shared utilities
```

### Adding a New Script
```
scripts/<category>/<name>.sh    # Implementation
scripts/<category>/README.md    # Usage docs
```

## Git Conventions

- **Commit messages:** `<type>: <description>` where type is feat, fix, docs, refactor, test, chore
- **Branch naming:** `feature/<name>`, `fix/<name>`, `research/<name>`
- **No commits without explicit request** from the operator

## Versioning

- Semantic versioning: `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes to data formats or module interfaces
- MINOR: New features, new indicators, new research findings
- PATCH: Bug fixes, documentation updates, config changes

## Review Checklist

Before merging or accepting changes:

- [ ] Follows module structure
- [ ] No sample code or placeholders
- [ ] No trading strategy logic
- [ ] Error handling present
- [ ] Type hints on Python functions
- [ ] Tests written or updated
- [ ] Documentation updated
- [ ] No secrets or credentials committed
