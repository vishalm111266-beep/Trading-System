# Amendment 004: Evidence-First Research Framework

**Date:** 2026-07-16
**Type:** Methodology + Configuration
**Status:** PROPOSED

## Change

Introduced automatic Evidence-First Research methodology via OpenCode ambient instructions:

1. Created `docs/evidence-first-framework.md` — single source of truth for evidence standards
2. Registered framework in `opencode.json` `instructions` array — automatically injected into all agent sessions
3. Updated `.opencode/agents/researcher.md` — clarified evidence-first responsibility
4. Updated `.opencode/skills/research-intake/SKILL.md` — reference global framework
5. Updated `.opencode/skills/deep-research/SKILL.md` — reference global framework

## Rationale

### Problem
Previous research workflows lacked systematic evidence ranking. Hallucinations occurred when low-tier evidence (community discussion) was treated as authoritative. No automatic mechanism prevented conclusions without evidence backing.

### Solution
Used OpenCode's ambient `instructions` mechanism to inject evidence standards into EVERY agent session automatically:
- No manual skill loading needed
- No routing logic needed
- Single source of truth in `docs/evidence-first-framework.md`
- Scales to all future research workflows

### Why Ambient Instructions Over Other Approaches

| Approach | Why Not | Why This Works |
|----------|---------|----------------|
| Duplicate logic in each skill | DRY violation, maintenance burden | Single document, zero duplication |
| Custom `.opencode/frameworks/` | Not officially supported | Uses official `instructions` field |
| New skill + manual loading | User must remember to invoke | Automatic, no user action needed |

## Key Features

✅ **Automatic**: No user needs to remember "use evidence-first"
✅ **DRY**: Single source of truth in one document
✅ **Scalable**: Future research skills inherit framework automatically
✅ **Official**: Uses only official OpenCode primitives
✅ **Efficient**: Instructions loaded once per session, shared across all uses
✅ **Hallucination-resistant**: Enforces evidence hierarchy, prevents tier-override, requires confidence assessment

## Impact

- All research-capable agents now automatically rank evidence by tier
- Tier 1 (official) always overrides Tier 4 (community)
- Conflicts between tiers are explicitly documented
- All conclusions must cite evidence sources
- Confidence is assessed based on evidence quality
- Unknown facts remain unknown (not invented)

## Implementation

No code changes. Pure configuration + documentation:
- Adds ~250 tokens to every research session (framework document)
- Tokens loaded once per session, shared across all agents
- Zero token waste from duplication

## Testing

To verify framework activation:
1. Ask researcher to "research X"
2. Check output includes evidence tiers and confidence assessment
3. Verify Tier 1 sources take precedence over Tier 4
4. Confirm conflicts are noted explicitly

## Rollback

If needed:
```bash
git checkout HEAD -- opencode.json docs/evidence-first-framework.md
rm docs/amendments/004-2026-07-16-evidence-first-research.md
```

## Future Improvements

- Consider evidence framework for non-research agents (architect, reviewer)
- Add evidence validation checklist skill
- Create confidence scoring thresholds
