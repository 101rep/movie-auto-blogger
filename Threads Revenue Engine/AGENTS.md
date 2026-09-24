# Project rules

- Do not remove existing functionality without cause.
- Never hardcode real API keys; all secrets use environment variables. Never commit .env.
- Every external request has a timeout; never swallow provider errors.
- A schedule record is not success. Require a remote Threads ID and verification before SUCCESS.
- Persist failure causes and use bounded retries; auth/permission errors need intervention.
- Prevent duplicate text across accounts and repeated products within cooldown.
- Block missing affiliate disclosure, fabricated experience, unverified discount/stock claims and copied source text.
- Treat mock results as mock, never live metrics.
- Run tests after changes; do not report completion with failing tests.
- Keep provider APIs isolated. Do not invent endpoints/permissions.
- Preserve audit logs and database records during emergency stop.
