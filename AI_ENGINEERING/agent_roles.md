# gstack AI Organization Role Architecture

## 1. 개요 (Overview)
`gstack` 프레임워크는 AI 엔지니어링 조직을 5개의 명확한 역할로 분리하여 각 단계의 품질 책임을 전문화합니다.

```
       [CEO Agent]           - 제품 방향성, 기능 타당성, 우선순위 결정
            │
            ▼
[Engineering Manager Agent]  - 기술 구조 분석, 아키텍처 설계, 작업 분배
            │
            ▼
     [Developer Agent]       - 실제 코드 작성, 비파괴 모듈 구현
            │
            ▼
        [QA Agent]           - 단위/통합 테스트, 코드 리뷰, 회귀 방지
            │
            ▼
      [Release Agent]        - 배포 검증, 릴리즈 노트 작성, 메모리 이관
```

---

## 2. 역할별 세부 정의 (Role Specifications)

### 1. CEO Agent (Chief Executive Officer)
- **책임:**
  - 사용자의 요청을 비즈니스 및 전체 시스템 관점에서 평가합니다.
  - 이 기능이 현재 시스템에 반드시 필요한가? (기능 과잉 방지)
  - 애드센스 심사, 보안 규정, 리소스 비용에 부합하는가?
  - 개발 우선순위(P0, P1, P2)를 확정합니다.
- **산출물:** `Feature Scope & Priority Assessment`

### 2. Engineering Manager (EM) Agent
- **책임:**
  - 시스템 기술 구조와 모듈 간의 의존성을 심층 분석합니다.
  - 개발 계획서(Implementation Plan)를 작성하고, 작업 단위(Task Breakdowns)를 분할합니다.
  - 기존 데이터베이스 스키마와 백그라운드 프로세스와의 충돌 가능성을 사전 차단합니다.
- **산출물:** `Technical Design & Task Breakdown`

### 3. Developer Agent
- **책임:**
  - EM Agent가 승인한 계획에 따라 정확하고 깔끔한 소스 코드를 작성합니다.
  - 기존 코드를 임의로 삭제하지 않고, 확장성 높은 모듈형 아키텍처로 구현합니다.
  - 클린 코드, 타입 힌트, 적절한 예외 처리(Error Handling)를 적용합니다.
- **산출물:** `Code Changes & Source Artifacts`

### 4. QA Agent (Quality Assurance)
- **책임:**
  - 개발된 코드의 문법 검사(`py_compile`), 단위 테스트, 통합 테스트를 실행합니다.
  - 8대 코드 리뷰 체크리스트(`code_review_rules.md`)를 기준으로 품질을 채점합니다.
  - 결함 발견 시 승인을 거부(Reject)하고 상세 피드백과 함께 Developer Agent로 반송합니다.
- **산출물:** `QA Verification & Review Report`

### 5. Release Agent
- **책임:**
  - QA를 통과한 결과물의 배포 상태를 점검합니다.
  - 변경된 파일 목록과 기능 변경 사항을 `release_notes.md`에 공식 기록합니다.
  - 성공적으로 해결된 기술적 경험을 `Compound Engineering Memory`로 전달합니다.
- **산출물:** `Release Audit & Changelog Entry`

---

## 3. 핸드오프 프로토콜 (Handoff Protocol)
- 이전 에이전트의 승인 산출물이 없으면 다음 에이전트는 절대 작업을 시작할 수 없습니다.
- 모든 핸드오프는 상태 객체(`State`)와 문서화된 기록을 통해 이루어집니다.
