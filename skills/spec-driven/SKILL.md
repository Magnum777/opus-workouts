---
name: spec-driven
description: "Spec-driven dev pipeline. Requirements > design > tasks > code. Steering files, hooks, works with any model."
---

# Spec-Driven Development

Structured development pipeline: define what you're building *before* you build it.

## When to Use

- New features or modules
- Greenfield projects
- Any task where correctness matters more than speed
- When user says "spec it," "spec-driven," or describes something they want built properly

**When NOT to use:** Quick bug fixes, one-liners, rapid prototyping where speed > precision.

## The Pipeline

Every feature goes through three phases before any implementation code is written. Each phase produces a markdown document that the user reviews and approves.

### Phase 1: Requirements Spec

Generate `specs/{feature-name}/requirements.md`:

```markdown
# Requirements: {Feature Name}

## Overview
{1-2 paragraph description of what this feature does and why}

## Functional Requirements
- FR-01: {requirement with acceptance criteria}
- FR-02: {requirement with acceptance criteria}

## Non-Functional Requirements
- NFR-01: {performance, security, compatibility constraints}

## Edge Cases
- EC-01: {what happens when...}

## Out of Scope
- {Explicitly excluded items}

## Acceptance Criteria
- [ ] {measurable condition for "done"}
```

**Rules:**
- Be specific. "The cart must persist across browser tabs" not "cart should work well"
- Include failure modes and error handling
- Every requirement must be testable
- List what is NOT being built (scope boundaries prevent scope creep)

### Phase 2: Design Spec

Generate `specs/{feature-name}/design.md` ONLY after requirements are approved:

```markdown
# Design: {Feature Name}

## Architecture Decision
{High-level approach: which components, patterns, data flow}

## Component Design
### {Component Name}
- Responsibility: {what it does}
- Interface: {inputs/outputs}
- Dependencies: {what it needs}
- State: {what it tracks}

## Data Model
{Schemas, types, database changes}

## API Contracts
{Endpoints, request/response shapes}

## Error Handling Strategy
{How errors propagate, retry logic, fallbacks}

## Security Considerations
{Auth, validation, sanitization}

## Trade-offs
| Decision | Chosen | Alternative | Reason |
|----------|--------|-------------|--------|
| {X} | {Y} | {Z} | {why Y over Z} |
```

**Rules:**
- Every design decision must reference a requirement (e.g., "Supports FR-03")
- Include alternatives you considered and why you rejected them
- If the design can't satisfy a requirement, flag it explicitly

### Phase 3: Task List

Generate `specs/{feature-name}/tasks.md` ONLY after design is approved:

```markdown
# Tasks: {Feature Name}

## Implementation Order
Tasks sequenced by dependency. Each task small enough for a single agent action.

### Task 1: {Name}
- **Depends on:** None
- **Touches:** {files/components}
- **Implements:** {FR-XX}
- **Verification:** {how to confirm it works}
- **Estimate:** {S/M/L}

### Task 2: {Name}
- **Depends on:** Task 1
- **Touches:** {files/components}
- **Implements:** {FR-XX}
- **Verification:** {how to confirm it works}
- **Estimate:** {S/M/L}

## Testing Plan
- Unit tests: {what to test at component level}
- Integration tests: {what to test across components}
- Property tests: {invariants that must hold for all inputs}

## Rollout Plan
- {How to deploy safely, feature flags, rollback}
```

**Rules:**
- Each task must be completable in a single focused session
- Every task references specific requirements and design decisions
- Include verification steps, not just implementation steps
- Order by dependency -- no task should depend on a later task

## Steering Files

Persistent project context stored in `.kiro/steering/` (compatible with Kiro's format):

### `.kiro/steering/product.md`
```markdown
# Product Context
## What this application does
{1-3 sentences}
## Who uses it
{Target users and their goals}
## Business constraints
{Budget, timeline, compliance, scale requirements}
```

### `.kiro/steering/techstack.md`
```markdown
# Tech Stack
## Languages & Runtimes
{What we use, versions}

## Frameworks & Libraries
{What we use, versions, and WHY}

## What we avoid
{Libraries/approaches explicitly excluded and why}
```

### `.kiro/steering/codingstandards.md`
```markdown
# Coding Standards
## Naming conventions
{variable, function, file naming rules}

## Error handling
{patterns for errors, logging, retries}

## Testing requirements
{what must be tested, minimum coverage}

## Code review checklist
{what reviewers check before approving}
```

**Usage:** When starting a spec-driven session, read all `.kiro/steering/*.md` files first. Their content informs every phase. If steering files don't exist, offer to create them before proceeding.

## Hooks (Event-Driven Automation)

Adapted from Kiro's hooks concept for OpenClaw. Define in `.kiro/hooks.json`:

```json
{
  "hooks": [
    {
      "name": "auto-test",
      "trigger": "file_save",
      "pattern": "**/*.py",
      "action": "Generate or update unit tests for the saved file"
    },
    {
      "name": "auto-types",
      "trigger": "file_save",
      "pattern": "**/*.ts",
      "action": "Update TypeScript type definitions and interfaces"
    },
    {
      "name": "auto-docs",
      "trigger": "file_save",
      "pattern": "**/*.py",
      "action": "Update docstrings and API documentation"
    }
  ]
}
```

**How to use:** After writing implementation code, check `.kiro/hooks.json` and execute matching hooks. Run hooks as sub-agent tasks when possible. Hook output is always presented for review -- never auto-committed.

## Workflow

1. **Check for steering files.** Read `.kiro/steering/*.md` if they exist. If not, offer to create them.
2. **Understand the feature.** Discuss with the user until the intent is clear.
3. **Write requirements.** Generate `specs/{name}/requirements.md`. Present to user. Wait for approval.
4. **Write design.** Generate `specs/{name}/design.md`. Present to user. Wait for approval.
5. **Write tasks.** Generate `specs/{name}/tasks.md`. Present to user. Wait for approval.
6. **Implement.** Execute tasks in order. After each task, run matching hooks from `.kiro/hooks.json`.
7. **Verify.** Run the testing plan from the task list. Property tests where possible.

## Anti-Patterns

- Don't skip phases. Writing code before requirements is the whole problem.
- Don't combine phases. Each document is a separate review checkpoint.
- Don't write vague requirements. "Should be fast" is not a requirement. "Page load under 2s at 1000 concurrent users" is.
- Don't implement without task reference. Every line of code should trace back to a requirement.
- Don't auto-approve. The user must explicitly approve each phase before proceeding.

## Model Notes

This skill works with any model. For spec generation (phases 1-3), prefer higher-reasoning models (kimi-k2.6, deepseek-v4-pro). For implementation tasks, use code-optimized models (glm-5.1, mimo-v2.5-pro). Steering files compensate for model quality -- a smaller model with good steering files outperforms a larger model without them.