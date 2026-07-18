---
name: research-intake
description: Structured research workflow for gathering and synthesizing information. Use when user says "research", "investigate", "find out", or "explore".
---

# Research Intake Skill

Structured approach to researching technical topics.

## Research Workflow

### Phase 1: Understand

Before researching, clarify:
1. What is the specific question?
2. What form should the answer take?
3. How detailed should the research be?
4. What constraints exist?

**If unclear, ask questions first.**

### Phase 2: Explore

Use search tools systematically:

```
1. Glob/Grep: Find existing related code in project
2. WebSearch: Find official documentation
3. WebFetch: Read specific docs or articles
```

### Phase 3: Analyze

- Extract key facts
- Note conflicting information
- Identify confidence levels
- Find specific examples

### Phase 4: Synthesize

Combine findings into:
1. **Summary** (1-2 sentences): What you found
2. **Key Facts**: Most important discoveries
3. **Details**: Specifics with locations/sources
4. **Recommendations**: What to do with the information

## Output Format

```
## Research Summary
[One sentence answer to the question]

## Key Findings
1. ...
2. ...
3. ...

## Details

### Finding 1: [Title]
- Source: [URL or file:line]
- What: [Specific information]
- Confidence: High/Medium/Low

### Finding 2: ...
...

## Recommendations
[What should be done based on research]

## Follow-up Questions
[Related questions that emerged]
```

## Research Rules

1. **Be specific**: Cite file paths, line numbers, URLs
2. **Be honest**: Note when information is uncertain
3. **Be complete**: Search before concluding "not found"
4. **Be concise**: Don't overwhelm with irrelevant details

## Evidence-First Framework

This skill automatically applies the Evidence-First Research framework defined in `docs/evidence-first-framework.md`. All research phases follow the evidence hierarchy (Tier 1 overrides lower tiers), and all outputs must include confidence assessment and unknown facts.