---
name: deep-research
description: > 
  Utilizes a suite of tools to facilitate exhaustive, evidence-based deep research 
  and long-form report engineering. Enforces a minimum 10-iteration search cycle, 
  recursive reflection, and the production of structured reports exceeding 10,000 
  words with mandatory IPython visualizations and specific paragraph logic.
---

# Deep Research Skill

## Overview
Execute a high-intensity research protocol focused on exhaustive discovery, continuous recursive reflection, and high-density analytical reporting. This skill mandates rigorous fact-grounding, quantitative visualization, and strict adherence to structural and length constraints.

### Evidence-First Compliance

This deep research protocol automatically adheres to the Evidence-First Research framework (see `docs/evidence-first-framework.md`). All 10+ search iterations prioritize Tier 1 evidence first, document conflicts when tiers disagree, and rate confidence based on evidence source authority.

## 📂 Output Path
Final report destination: `/mnt/agents/output/report.md`

## 🚀 Research & Discovery Phase (The 10+ Step Loop)

### Iterative Search Protocol
1. **Perform at least 10 search steps** to ensure comprehensive coverage across multiple dimensions
2. **Avoid keyword redundancy**; ensure each round brings substantial new information
3. **Credibility & Verification**: Prioritize authoritative sources (government sites, academic databases, peer-reviewed journals)
4. **Never fabricate data**. Every statistic and claim must be accurate and traceable

### Recursive Reflection (After EACH Search Round)

**Thinking Process:**
- Reflect on content found
- Identify unmet needs
- Plan the next specific step

**Summary:**
- Concise recap of key findings

**Constraint:** Both sections must be short and concise.

### Quantitative Analysis
- Prioritize programming tools for calculations
- Actively use IPython to generate charts, graphs, and data visualizations
- Embed these directly into the Markdown

## 📝 Report Engineering Standards

### 1. Structural Logic & Opening

**Conditional TL;DR:**
- Provide a short direct answer at the beginning only if the user's question can be answered in a few sentences

**Style Adaptation:**
- If a specific style is implied (e.g., story, interview, case narrative), adhere to it
- Default: Strict academic report format
- Omit generic Introduction/Background sections unless explicitly required

### 2. Depth and Analysis (Mode-Based)

**Academic/Survey Mode:**
- Prioritize comprehensive fact-based detail
- Include full definitions, formulas, statistical indicators (CI, metrics), and baseline comparisons
- Avoid speculative interpretation; ensure all statements are supported by references

**Lifestyle/Practical Mode:**
- Incorporate observations, human insights, Pros/Cons, and actionable trade-offs
- Reflect on implications and explain why certain patterns matter

### 3. Length and Paragraph Constraints

**Total Volume:** The final report must exceed 10,000 words.

**Paragraph Rules:**
- Each paragraph must be at least 100 words (max 1,000 words)
- **Subsection Rule:** Every subsection (e.g., ## 3.1) MUST contain more than one paragraph
- **Natural Transitions:** In English writing, avoid rigid patterns like "First, second, third" or "Firstly, secondly, lastly"

### 4. Mandatory Table Architecture

**Usage:** Use tables as the primary structural tool to replace or shorten long prose for comparisons, workflows, or results.

**Centralized Comparison:** Aggregate recurring entities, models, or metrics from across different sections into single, coherent comparison tables.

**Source Integration:** Do not include a separate "Source" column. Place numeric citations (e.g., [^1^]) directly within the data cells.

## ⚖️ Formatting & Citation Rules

### Citation Format
- Use [^index^] for factual/formal pieces
- Max two citations per sentence
- Note: Do not use citations for creative/non-formal writing

### Bolding Strategy
- **Bold important keywords, critical numbers, major conclusions, and key insights**
- **Avoid redundant bolding:** Do not repeatedly bold the same entity within a short span

### Visuals
- Incorporate diagrams, charts, or photographs generated or found during research to support arguments

### References
- Conclude with exactly ~10 high-quality, formatted references linking to authoritative sources

## 🛠 Execution Workflow

### Phase 1: Explore
- Conduct a minimum of 10 search rounds with concise recursive reflections

### Phase 2: Visualize
- Perform IPython-based data analysis and embed generated charts

### Phase 3: Write
- Generate the article at `/mnt/agents/output/report.md` following the word count and multi-paragraph subsection rules

## 🔍 Search Strategy Template

### Round 1: Initial Discovery
**Search Query:** [Primary topic + broad context]
**Thinking:** What foundational information is needed? What are the key concepts?
**Summary:** Core definitions, scope, and basic framework identified.

### Round 2: Deep Dive - Core Concepts
**Search Query:** [Specific aspect + academic/research focus]
**Thinking:** What technical details are missing? What formulas/metrics matter?
**Summary:** Technical specifications, mathematical foundations identified.

### Round 3: Comparative Analysis
**Search Query:** [Comparison + benchmark data]
**Thinking:** How do different approaches compare? What are the trade-offs?
**Summary:** Performance comparisons, pros/cons analysis completed.

### Round 4: Real-World Applications
**Search Query:** [Case studies + implementation examples]
**Thinking:** What practical evidence exists? What are the success patterns?
**Summary:** Implementation examples, case studies gathered.

### Round 5: Risk & Limitations
**Search Query:** [Risk factors + failure modes + limitations]
**Thinking:** What can go wrong? What are the boundaries?
**Summary:** Risk matrix, limitation analysis documented.

### Round 6: Market/Industry Context
**Search Query:** [Market data + industry trends + adoption rates]
**Thinking:** What is the market size? Who are the key players?
**Summary:** Market analysis, competitive landscape mapped.

### Round 7: Regulatory & Compliance
**Search Query:** [Regulations + standards + compliance requirements]
**Thinking:** What legal framework governs this? What standards apply?
**Summary:** Regulatory landscape, compliance requirements identified.

### Round 8: Future Trends
**Search Query:** [Emerging technologies + future projections + roadmap]
**Thinking:** Where is this heading? What innovations are coming?
**Summary:** Trend analysis, future outlook synthesized.

### Round 9: Cross-Reference Validation
**Search Query:** [Verify key claims + cross-reference statistics]
**Thinking:** Are the numbers consistent across sources? What needs verification?
**Summary:** Data validation completed, discrepancies resolved.

### Round 10: Synthesis & Gap Analysis
**Search Query:** [Fill remaining gaps + final verification]
**Thinking:** What still needs clarification? Is the picture complete?
**Summary:** All gaps filled, comprehensive understanding achieved.

## 📊 Visualization Requirements

### Mandatory Charts
1. **Performance Comparison Bar Chart** - Compare key metrics across alternatives
2. **Trend Line Chart** - Show historical patterns and projections
3. **Risk Matrix Heatmap** - Visualize risk assessment
4. **Market Share Pie Chart** - Show competitive landscape
5. **Flowchart** - Illustrate processes or decision trees

### IPython Code Template
```python
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Example: Performance Comparison
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Chart 1: Bar comparison
axes[0,0].bar(categories, values, color='steelblue')
axes[0,0].set_title('Performance Comparison')
axes[0,0].set_ylabel('Score')

# Chart 2: Trend line
axes[0,1].plot(dates, trend_data, marker='o')
axes[0,1].set_title('Historical Trend')

# Chart 3: Risk heatmap
im = axes[1,0].imshow(risk_matrix, cmap='RdYlGn_r')
axes[1,0].set_title('Risk Assessment')

# Chart 4: Distribution
axes[1,1].hist(distribution_data, bins=20, alpha=0.7)
axes[1,1].set_title('Distribution Analysis')

plt.tight_layout()
plt.savefig('/mnt/agents/output/visualizations.png', dpi=300, bbox_inches='tight')
plt.show()
```

## 📋 Report Structure Template

```markdown
# [Title]

## Executive Summary
[Conditional TL;DR - only if applicable]

## 1. [Core Topic]
### 1.1 [Subsection]
[Multiple paragraphs, 100+ words each]

### 1.2 [Subsection]
[Multiple paragraphs, 100+ words each]

## 2. [Comparative Analysis]
### 2.1 [Subsection]
[Include comparison table]

### 2.2 [Subsection]
[Multiple paragraphs]

## 3. [Technical Deep Dive]
### 3.1 [Subsection]
[Formulas, metrics, specifications]

### 3.2 [Subsection]
[Implementation details]

## 4. [Applications & Case Studies]
### 4.1 [Subsection]
[Real-world examples]

### 4.2 [Subsection]
[Success patterns]

## 5. [Risk & Limitations]
### 5.1 [Subsection]
[Risk matrix]

### 5.2 [Subsection]
[Failure modes]

## 6. [Market Context]
### 6.1 [Subsection]
[Market data, trends]

### 6.2 [Subsection]
[Competitive landscape]

## 7. [Future Outlook]
### 7.1 [Subsection]
[Emerging trends]

### 7.2 [Subsection]
[Projections]

## 8. [Conclusion]
[Key insights, final recommendations]

## References
[^1^]: [Source 1]
[^2^]: [Source 2]
...
[^10^]: [Source 10]
```

## ⚠️ Quality Checklist

Before finalizing the report, verify:

- [ ] Minimum 10,000 words
- [ ] At least 10 search rounds completed
- [ ] Recursive reflection after each search
- [ ] All paragraphs 100+ words
- [ ] Every subsection has multiple paragraphs
- [ ] Tables used for comparisons
- [ ] IPython visualizations embedded
- [ ] Citations in [^index^] format
- [ ] ~10 high-quality references
- [ ] No fabricated data
- [ ] Natural transitions (no "First, second, third")
- [ ] Bold used strategically (no redundancy)
- [ ] Report saved to /mnt/agents/output/report.md
