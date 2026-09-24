# Publishing engine

Post/Job lifecycle: GENERATED/DRAFT → VALIDATING → READY → SCHEDULED → PUBLISHING → PUBLISHED → VERIFYING → SUCCESS. Cancellation is allowed before remote publication. Failures record error codes and JobAttempt records; transient failures get 60/300/1800-second delays, then FAILED. Authentication failures require operator action. FAILED is the terminal equivalent of FAILED_FINAL in this version.

Explicit human approval is mandatory. Edits invalidate approval. Exact fingerprints are globally reserved; recent text/hook similarity is checked. Each worker claim uses a database lease with an owner token. The mock provider stores unique post/reply idempotency keys outside the worker transaction. Every reply references the previous remote ID. SUCCESS requires all IDs and verification.

Stop/account status are reread between writes. In-flight operations cannot be recalled. Lost leases cannot initiate new writes. Crash recovery repeats only uncheckpointed calls with the same idempotency key. Verified SUCCESS with unfinished bookkeeping is reconciled after lease expiry.

Before live operation, reconcile ambiguous remote outcomes and prove provider recovery. PostgreSQL concurrency and SQLite busy behavior need deployment/load tests. Live Threads endpoints remain unimplemented.
