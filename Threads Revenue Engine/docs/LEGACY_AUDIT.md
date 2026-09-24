# Legacy audit — 2026-09-23

The supplied workspace contained only empty work/ and outputs/ directories. No application, repository files, database, or credentials were supplied. The attached master prompt is the specification, not legacy code.

| Module | Decision | Evidence |
|---|---|---|
| Threads/auth/replies, scheduler, Telegram | REPLACE (new implementation) | No source present |
| Coupang/Naver/Gemini adapters | REPLACE (new interfaces and explicit stubs) | No source present |
| Database/logging/worker/UI | REPLACE (new implementation) | No source present |

REUSE: none. REFACTOR: none. No existing features or files were removed.

Initial scope: phases 0–3, phase 4 mock publishing, phase 5 basic command and notification structure. Live provider implementations, revenue analytics, learning and production readiness are later work.
