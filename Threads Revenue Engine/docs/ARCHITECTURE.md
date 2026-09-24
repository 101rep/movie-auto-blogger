# Architecture

Next.js/TypeScript administrator client → authenticated FastAPI → SQLAlchemy repositories/services → durable database job queue → separate polling worker → provider adapters.

SQLite supports local development; PostgreSQL supports deployment. UTC timestamps are stored as timezone-aware values through a portable SQLAlchemy type. Account timezone controls daily limits. Alembic owns schema creation.

DB jobs are the source of truth. A compare-and-set claim prevents two workers claiming the same job. A committed checkpoint stores each mock remote ID. The mock remote store has unique idempotency keys, so interrupted jobs can resume without duplicate posts/replies. Real providers must implement reconciliation for ambiguous outcomes before they can be enabled.

RQ/Redis transport is optional: dispatcher enqueues durable job identifiers; the same worker claim handles duplicate delivery. A DB polling mode provides the offline path. Redis loss does not lose jobs. Compose uses Redis and RQ.

Authentication uses PBKDF2 password hashes, expiring opaque bearer sessions stored only as SHA256 hashes, logout/revocation and DB-backed login throttling. The browser keeps its bearer in memory; no ambient authentication cookie means CSRF cannot authorize an API request. CORS has an explicit development origin. Production requires TLS, private backend/Redis/Postgres and strong administrator credentials.

Kill switch and account pause are checked before each external write. An already in-flight request cannot be recalled. Every external provider call must have a timeout. Live adapters fail closed with NOT_IMPLEMENTED; no invented endpoints. Mock results are visibly tagged in DB, UI and notifications.

Layer boundaries: apps/backend/tre (API, models, services), services (provider contracts and mock implementations), apps/worker (dispatcher/worker), apps/frontend (UI), tests, docs, docker, scripts.

Design limitations: content heuristic checks assist human review; they cannot prove truthfulness or copyright compliance. Human approval is required before scheduling. Local development is single-host. Live posting remains disabled pending official API contract verification and crash/reconciliation review.
