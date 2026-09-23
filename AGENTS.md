# Antigravity Workspace Multi-Agent Specification (gstack & Superpowers)

## 1. AI Engineering Organizational Hierarchy
모든 엔지니어링 및 개발 작업은 아래 5단계 전문 역할에 의해 수행됩니다:

1. **CEO Agent**:
   - 비즈니스 정합성, 기능의 실질적 필요성 검토, 우선순위 확정.
   - 불필요한 기능 추가 및 과잉 엔지니어링 방지.
2. **Engineering Manager (EM) Agent**:
   - 시스템 아키텍처 및 모듈 의존성 분석.
   - 작업 분할 및 기술 구현 계획서(`implementation_plan.md`) 작성.
3. **Developer Agent**:
   - 비파괴 모듈식 코드 작성, 기존 운영 코드 삭제 금지.
   - 클린 코드, Windows UTF-8 호환성, 비동기 스레드 분리 준수.
4. **QA Agent**:
   - 8대 자동 코드 리뷰 체크리스트(`AI_ENGINEERING/code_review_rules.md`) 수행.
   - 구문 컴파일, 회귀 테스트, DOM 렌더링 검증.
5. **Release Agent**:
   - 배포 점검, 체인지로그(`AI_ENGINEERING/release_notes.md`) 업데이트.
   - 장애 원인 및 해결책을 `Compound Engineering Memory`로 전달.

## 2. Superpowers 개발 파이프라인
모든 개발 요청은 즉흥적 코드 작성을 금지하며, 다음 7단계를 강제합니다:
`Request` -> `Problem Analysis` -> `Plan` -> `Implementation` -> `Testing` -> `Verification` -> `Report`

## 3. Compound Engineering 학습 루프
- 과거 해결된 모든 이슈(RCA)는 `AI_ENGINEERING/debugging_history.md`에 보존됩니다.
- 새로운 버그 발견 시 동일한 원인의 반복 발생 여부를 먼저 확인하고, 해결 후 즉시 지식베이스에 추가합니다.
