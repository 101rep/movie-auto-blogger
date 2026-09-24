# Content engine

Manual source ingestion is functional. Other source types can be registered as metadata; auto-fetch is deferred. Provider interfaces expose fetch/normalize/validate/deduplicate. Normalized hashes prevent duplicate sources.

Mock analysis returns evidence/reliability/risk flags and account scores tagged mock. Mock writing is a deterministic workflow template, not production-quality AI. Gemini is explicitly unimplemented.

Humanizer checks length, line length, emoji, hashtag, phrases, endings, tone heuristic, specific detail heuristic, recent hook/text similarity and source overlap. Safety blocks known unverified usage/discount/stock/medical claims. PASS is required for approval and scheduling. Heuristics cannot prove originality or factuality: human review remains required.

Goal, angle and hook enums are supported by API. Persona/content ratios are editable. Affiliate ratio uses a conservative rolling 20-post window: at 20%, start with 4 information posts before the first affiliate post. Goal-based editorial planning and automatic rewriting remain future enhancements.
