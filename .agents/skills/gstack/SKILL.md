---
name: gstack
description: >-
  gstack AI Engineering Organization Role Management framework.
  Separates development into 5 specialized intelligence roles:
  CEO Agent, Engineering Manager (EM) Agent, Developer Agent,
  QA Agent, and Release Agent.
---

# gstack AI Role Management Skill

## Trigger Conditions
Activate this skill for complex architectural changes, new feature additions, system refactorings, or production releases.

## Role Responsibilities & Handoff Pipeline

### 1. CEO Agent
- Evaluates strategic necessity and business priority.
- Answers: "Is this feature necessary? Does it respect resource budgets, security rules, and AdSense isolation?"
- Outputs: Feature Scope and Approval.

### 2. Engineering Manager (EM) Agent
- Performs deep technical analysis of module boundaries and dependencies.
- Writes detailed implementation specifications and breaks work into tasks.
- Prevents database or runtime collisions.

### 3. Developer Agent
- Implements the approved design with clean, modular, and non-destructive code.
- Follows existing conventions and avoids redundant dependencies.

### 4. QA Agent
- Audits changes against the 8-pillar code review standard (`/AI_ENGINEERING/code_review_rules.md`).
- Executes syntax validation, unit tests, and live edge-case verification.
- Rejects code if any blocker or test failure is found.

### 5. Release Agent
- Verifies post-test stability and deployment status.
- Updates changelog in `release_notes.md`.
- Hands off lessons learned to the Compound Engineering learning loop.
