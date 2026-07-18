# YouTube Transcript Analysis

Analyzes YouTube video transcripts to extract key points, strategies, and actionable insights.

## When to Use

Use this skill when user:
- Pastes or uploads a YouTube transcript
- Says "analyze this video", "extract key points from transcript"
- Wants to understand strategies discussed in a video
- Needs to learn from trading/financial YouTube content

## Analysis Framework

### 1. Topic Identification
- What is the main theme/topic of the video?
- Who is the speaker and their expertise level?
- What is the target audience?

### 2. Key Points Extraction
- Main thesis or argument presented
- Supporting evidence or data points
- Important definitions or concepts
- Timestamps of significant moments (if available)

### 3. Strategy Identification (for trading/financial content)
- Entry criteria for trades
- Exit strategies
- Risk management rules
- Position sizing approaches
- Market conditions that trigger decisions
- Indicators or tools mentioned
- timeframe preferences

### 4. Actionable Insights
- What can be directly applied?
- What requires further research?
- Any proven backtested results mentioned?
- Warnings or common mistakes to avoid

### 5. Summary & Recommendations
- 3-5 bullet point summary
- Credibility assessment (based on speaker, data provided, results shown)
- Follow-up resources or videos suggested

## Output Format

```
## Video Analysis: [Video Title/Topic]

### Overview
- **Speaker**: [Name/Channel if known]
- **Duration**: [If timestamp available]
- **Topic**: [Main theme]

### Key Points
1. [Point 1]
2. [Point 2]
3. [Point 3]

### Strategies Discussed
**[Strategy Name]**
- Entry: [Criteria]
- Exit: [Criteria]
- Risk: [Management approach]
- Timeframe: [Applicable timeframe]

### Actionable Takeaways
- ✅ [可直接应用的]
- ⚠️ [需要进一步验证的]
- 📚 [需要学习的]

### Credibility Score: [High/Medium/Low]
[Reasoning]

### Related Strategies in Our System
[Link to any matching strategies we have]
```

## Important Notes

- If transcript is incomplete, note what information is missing
- If speaker makes claims without data, flag as "unverified"
- Always distinguish between opinion vs. proven strategies
- For backtestable strategies, suggest adding to @backtest-engineer workflow
- If strategy conflicts with existing ones, note the conflict

## Integration with Other Agents

After analysis:
- If strategy found → Invoke @strategy-developer to formalize rules
- If backtestable claims → Invoke @backtest-engineer to verify
- If risk management discussed → Invoke @risk-manager to assess
- If stock mentioned → Route to appropriate market expert

## Usage Example

When user pastes a transcript, load this skill and respond with:

"I've loaded the YouTube transcript analysis skill. Let me analyze this transcript for key points and strategies discussed."

Then perform the analysis following the framework above.