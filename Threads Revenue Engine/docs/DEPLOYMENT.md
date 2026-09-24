# Deployment

Local: Python 3.12, Node 22+, pnpm, SQLite, separate worker. Docker Compose: PostgreSQL 16, Redis 7/RQ, FastAPI, Next.js and dispatcher. Host ports bind loopback. Put a TLS reverse proxy in front of a deployed frontend; keep DB, Redis and backend private.

Set a unique ADMIN_PASSWORD (16+ characters) and POSTGRES_PASSWORD (URL-safe characters; otherwise encode the URL). Secrets never go in images/source control. Tokens are environment variable references. Seed preserves existing users: changing ADMIN_PASSWORD after seeding does not replace their stored password.

Run migrations before workers. Back up PostgreSQL, test restoration and monitor heartbeat/queue/notifications. Multi-host operation and outage recovery need deployment testing. Docker/PostgreSQL are supplied but not claimed verified unless the build report confirms it.

Sessions are expiring, revocable opaque bearer tokens held in browser memory, not localStorage. Cookie authentication is not accepted, so ambient-cookie CSRF cannot authorize mutations. Login throttling is DB-backed. Add edge request limits and trusted proxy handling before public exposure. Multi-user RBAC is deferred.

Official references checked: https://nextjs.org/docs/app/getting-started/installation and https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ (this implementation uses opaque sessions rather than JWT).
