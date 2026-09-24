# Affiliate boundary

CoupangProvider and NaverShoppingProvider are fail-closed stubs. Credentials alone do NOT enable integrations. Official access, endpoint contracts, permissions, signing and attribution must be implemented and verified later.

A mock product with example.invalid URLs is seeded. Product association, disclosure, affiliate URL, rolling affiliate ratio, per-day affiliate limit and 14-day cooldown are enforced. Product metadata persists as a cache foundation. Live search/deeplink/reports, ranking and administrative cooldown override are Phase 6 work. Missing metrics remain null.

Disclosure is configurable and must be checked against the applicable provider policy before live use. This foundation has one global template; provider-specific templates belong to Phase 6.
