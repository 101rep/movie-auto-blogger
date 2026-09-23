# Superpowers Workflow Rules (AI Engineering Operating Standard)

## 1. 핵심 철학 (Core Philosophy)
AI가 즉흥적으로 코드를 수정하거나 사전 분석 없이 파일을 변경하는 행위를 절대 금지합니다.
모든 개발 및 유지보수 작업은 반드시 **Superpowers 7단계 엔지니어링 프로세스**를 엄격히 준수합니다.

---

## 2. 7단계 표준 개발 프로세스 (The 7-Step Engineering Pipeline)

```
[1. Request]
    │  사용자 요구사항 접수 및 핵심 의도 파악
    ▼
[2. Problem Analysis]
    │  현상 분석, 기존 코드 영향도 평가, 기술적 제약조건 및 부작용 검토
    ▼
[3. Plan]
    │  구체적인 아키텍처 설계, 수정/신규 파일 정의, 롤백 전략 수립
    ▼
[4. Implementation]
    │  계획에 따른 점진적 비파괴(Non-Destructive) 코드 작성
    ▼
[5. Testing]
    │  단위 테스트, 정적 분석(Syntax & Lint), 통합 테스트 실행
    ▼
[6. Verification]
    │  실제 플랫폼 및 브라우저 DOM 렌더링 검증, 성능 및 로그 확인
    ▼
[7. Report]
    │  변경 파일 목록, 테스트 결과, 운영 지침을 담은 최종 보고서 작성
```

---

## 3. 절대 금지 항목 (Strict Prohibitions)

1. **분석 없는 코드 수정 금지 (No Coding Without Analysis)**
   - 요구사항을 받자마자 코드를 수정하지 않습니다. 문제의 근본 원인과 시스템 전반에 미칠 파급효과를 먼저 서술해야 합니다.
2. **영향도 확인 없는 파일 변경 금지 (No Blind File Modifications)**
   - 어떤 함수, 모듈, 데이터베이스 스키마가 영향을 받는지 사전에 목록화하지 않고 파일을 건드리지 않습니다.
3. **테스트 없는 완료 보고 금지 (No Completion Report Without Verification)**
   - 실제 터미널 실행 또는 자동화 테스트 결과 없이 "수정되었습니다"라고 보고하는 것을 엄격히 금지합니다.
4. **기존 운영 코드 임의 삭제 금지 (Zero Deletion of Functional Code)**
   - 기존의 자동화 로직이나 데이터 모델을 파괴하지 않고, 모듈 분리와 확장(Extension) 방식으로 구현합니다.

---

## 4. 프로세스 강제 장치 (Enforcement Mechanism)
- 모든 개발 시작 시 `Superpowers Hook`이 동작하여 사전 분석 및 계획 산출물이 생성되었는지 확인합니다.
- 사전 분석이 누락된 커밋이나 코드 변경은 QA Agent 단계에서 반려(Reject)됩니다.
