# Test plan

Run python -m pytest -q. Tests use isolated SQLite databases and mock providers. Coverage: models/seed, authenticated E2E, approval gating, cross-account duplicate, humanizer/safety, source copy, disclosure/cooldown, timezone/future jobs, emergency stop, stop between main/reply, bounded retry, expired token, reply recovery, idempotency conflict, Telegram authorization, health/logout, ratios, edit invalidation and account/Persona CRUD.

Run python scripts/e2e.py against a local API (E2E_URL can override its address). It logs in, creates/analyzes source, generates/validates/approves/schedules, invokes a separate worker process, and asserts remote IDs, replies, notification and dashboard. Use a fresh DB for repeatable runs.

Frontend: pnpm build/typecheck; browser login, navigation, review/schedule, dashboard reflection, mobile overflow and console errors. PostgreSQL/RQ/container verification is separate; SQLite alone does not prove it.
