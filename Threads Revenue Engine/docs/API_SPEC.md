# API specification

All /api routes except POST /api/auth/login require Authorization: Bearer <session>. OpenAPI at /docs is the authoritative typed schema. Lists are bounded for the initial version.

- POST /api/auth/login, POST /api/auth/logout, GET /api/auth/me
- GET/POST /api/accounts; PATCH/DELETE /api/accounts/{id}; GET/PUT /api/accounts/{id}/persona
- GET/POST /api/sources; GET/POST /api/content; POST /api/content/{id}/analyze; POST /api/content/{id}/generate
- GET /api/posts; PATCH /api/posts/{id}; POST /api/posts/{id}/validate; POST /api/posts/{id}/approve; POST /api/posts/{id}/schedule; POST /api/posts/{id}/cancel; POST /api/posts/{id}/retry
- GET /api/schedules, /api/products, /api/analytics, /api/logs, /api/telegram
- POST /api/telegram/command (authenticated simulator, allowed_chat_id enforced)
- GET/PATCH /api/settings; GET /api/system; POST /api/system/stop; POST /api/system/resume
- GET /health; GET /health/{db,redis,worker,threads,telegram,ai} (details authenticated)

Scheduling accepts timezone-aware scheduled_at or window_start/window_end with bounded jitter. READY plus explicit approval is required. Safety/duplicate/cooldown checks rerun before scheduling and publishing. Invalid transitions return 409/422, never success.
