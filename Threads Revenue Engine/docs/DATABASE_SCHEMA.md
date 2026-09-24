# Database schema

Account 1:1 Persona; ContentSource 1:N ContentItem; ContentItem 1:1 ContentAnalysis; ContentItem 1:N Post (draft lifecycle); Account 1:N Post; Post 1:N PostReply; Post 1:1 Job; Job 1:N JobAttempt; Post 1:N Notification; Account N:M Product through AccountProductHistory.

Post merges ContentDraft and Schedule: body, goal, angle, hook, validation JSON, approval timestamp, scheduled_at, fingerprint, status, remote_id, error and retry fields. This avoids duplicate mutable content records. Product stores provider/external ID, price/review metadata and explicitly identified mock affiliate URLs. AffiliateLink is part of Product in this initial scope.

User and Session implement authentication. LoginAttempt implements shared rate limiting. SystemSetting stores operational limits/disclosures/kill switch. AuditLog stores actor/action/target/request ID. JobAttempt stores failure code and time. WorkerHeartbeat records real worker liveness. MockRemotePost is a persistent simulated external store with a UNIQUE idempotency key. Notification is an outbox with delivery state.

Post fingerprint is globally unique for non-cancelled publishing reservations via a separate PublicationReservation table; cancelled draft content can be edited and reviewed again. Jobs have a unique post_id. Replies have unique (post_id, position). Product has unique (provider, external_product_id). Tokens are environment variable references only. No raw provider credentials or session tokens enter the database.

PostAnalytics and learning recommendations are explicitly deferred (phases 7–8); absent metrics remain null, never fabricated.
