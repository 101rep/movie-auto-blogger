# Telegram basic structure

Authenticated POST /api/telegram/command is an administrator simulator. It checks TELEGRAM_ALLOWED_CHAT_ID and supports /status /accounts /today /scheduled /failed /retry ID /pause ID /resume ID /revenue /help. Unknown, natural-language and destructive bulk commands are rejected. Global resume is only available through authenticated admin API/UI.

Notifications form a durable outbox. Publishing success is independent of delivery. Mock sends store a deterministic mock ID; failures have their own status/error. Live polling/webhook and sendMessage are unimplemented. No real recipient was contacted.

A future natural-language layer can map to typed commands; destructive commands need an explicit confirmation protocol before enablement.
