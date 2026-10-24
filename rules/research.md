# Research Rules

## Output Format
- Filename: `YYYY-MM-DD-<kebab-slug>.md`
- Always include YAML frontmatter: tags, date, sources_used, confidence

## Source Priority
- Data questions: primary sources first (central banks, FRED, BIS, IMF)
- Analysis questions: quality journalism first (FT, Bloomberg, Reuters)
- Always cite sources with URLs
- Flag confidence: high/medium/low based on source quality and recency

## API / Data Source Research
- When compiling lists of sources, APIs, or endpoints: **always test the actual endpoint** before documenting the data format. Don't rely on secondary research alone.
- Hit the endpoint, verify the response schema, record the real fields/format.
- If the verified response differs from what documentation claims, update the reference with the verified data.
- Mark each source with verification status (verified date, or "unverified").

## Synthesis Rules
- Never call external LLM APIs for synthesis — do it yourself
- Include specific numbers, dates, statistics — no vague summaries
