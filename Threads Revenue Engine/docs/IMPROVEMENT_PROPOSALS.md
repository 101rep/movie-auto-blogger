# Improvement proposals

## Durable database jobs
Current: Redis queue was suggested as the primary transport.
Problem: Redis is not guaranteed on Windows; queue and schedule writes can diverge.
Proposed: durable DB jobs, conditional claims and optional RQ execution ticks.
Benefits: offline E2E, visible state, recoverable delivery.
Risks: polling contention and lease/reconciliation testing.
Migration Cost: low for a new repository.
Recommendation: applied; load-test PostgreSQL/RQ before production.

## Unified draft/post/schedule row
Current: three suggested mutable entities.
Problem: approval can drift from scheduled content.
Proposed: one Post lifecycle with approval invalidation and separate replies.
Benefits: one content version and explicit transitions.
Risks: multi-editor history will need immutable revisions.
Migration Cost: low.
Recommendation: applied; add immutable revisions before multi-editor workflows.
