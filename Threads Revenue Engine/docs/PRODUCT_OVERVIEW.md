# Threads Revenue Engine

여러 Threads 브랜드 계정을 운영하는 관리자 전용 기반 시스템입니다. 계정 수는 제한하지 않으며 개발 seed만 7개입니다. 이번 구현 범위는 Phase 0–3, Mock 게시와 기본 Telegram 구조입니다.

소재 등록 → Mock 분석/계정 매칭 → 초안 → 편집 → 검사 → 사람 승인 → 예약 → 별도 Worker → Mock 본문/댓글 → 조회 검증 → SUCCESS → Mock Telegram outbox → 대시보드.

운영 데이터와 seed를 구분합니다. Mock 성과 지표를 만들지 않습니다. 수익/학습 기능은 이후 Phase 6–8의 범위입니다. 실제 API 승인을 받았거나 연결되었다고 주장하지 않습니다.
