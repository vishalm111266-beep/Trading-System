# Web Search Skill

Use this skill when you need to search the web for stock market information, news, or research.

## Available MCP Servers

### Exa MCP (Primary Search)
- **URL**: https://mcp.exa.ai/mcp
- **Status**: Connected and available

#### Available Tools:
- `web_search_exa` - Search the web for any topic
- `web_fetch_exa` - Get full content from a specific URL
- `web_search_advanced_exa` - Advanced search with filters (domains, dates, categories)

### Context7 MCP (Documentation)
- **URL**: https://mcp.context7.com/mcp
- **Status**: Connected and available

#### Available Tools:
- `context7_search` - Search documentation

## Usage Instructions

### For Stock Research
When researching stocks, use the Exa MCP tools:

```
Use web_search_exa with query like:
- "AAPL stock news 2024"
- "RELIANCE Q4 earnings analysis"
- "NVDA AI chip demand analysis"
```

### For Market News
```
Use web_search_advanced_exa with category: "news" for news articles
Use web_search_exa for general searches
```

### For Company Information
```
Use web_search_advanced_exa with category: "company" for company profiles
```

### For Fetching Specific Pages
```
Use web_fetch_exa to get content from a specific URL
```

## Examples

### Example 1: Search for stock news
```
web_search_exa {
  "query": "TESLA stock analysis July 2024",
  "numResults": 10
}
```

### Example 2: Advanced search with date filter
```
web_search_advanced_exa {
  "query": "Federal Reserve interest rate decision impact",
  "category": "news",
  "startPublishedDate": "2024-01-01",
  "numResults": 15
}
```

### Example 3: Fetch specific webpage
```
web_fetch_exa {
  "url": "https://www.example.com/article",
  "textMaxCharacters": 5000
}
```

## Tips
- Be specific in queries for better results
- Use date filters for recent information
- Use category filters to narrow results (company, news, research paper, etc.)