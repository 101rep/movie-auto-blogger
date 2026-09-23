---
name: superpowers
description: >-
  Superpowers development process workflow controller for AI coding assistants.
  Enforces a strict 7-step engineering pipeline: Request -> Problem Analysis ->
  Plan -> Implementation -> Testing -> Verification -> Report. Prohibits any
  blind code modification without analysis, impact assessment, or automated testing.
---

# Superpowers Workflow Control Skill

## Trigger Conditions
Activate this skill whenever a software development, debugging, refactoring, feature addition, or system maintenance request is received.

## Mandatory Execution Workflow
Before modifying any source code, you MUST follow these sequential phases:

### Phase 1: Request Understanding
- Parse the user's intent, core objectives, and explicit operational constraints.

### Phase 2: Problem & Impact Analysis
- Inspect the codebase.
- Identify all affected files, modules, database tables, and runtime services.
- Assess risks and potential side effects.

### Phase 3: Detailed Implementation Plan
- Formulate a precise, step-by-step technical plan before writing code.
- Define what files will be created or modified.

### Phase 4: Implementation
- Implement non-destructive, modular, well-typed code following clean code standards.
- Never delete working legacy code without explicit instruction.

### Phase 5: Automated Testing
- Compile and run unit tests, syntax checks (`py_compile`), and integration scripts.
- Fix all detected regressions immediately.

### Phase 6: Verification
- Verify that live services, rendered DOMs, and logs reflect expected behavior.

### Phase 7: Completion Report
- Report changed files, verification results, and operational instructions.

## Prohibitions
1. No coding without prior problem analysis.
2. No file editing without impact assessment.
3. No completion claims without automated test execution.
