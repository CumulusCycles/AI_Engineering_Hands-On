# Global Claude Guidance

## Working Style

- Prefer small, reviewable changes over large sweeping edits.
- State assumptions explicitly when requirements are unclear.
- After each meaningful change, run relevant checks (lint/tests) before declaring done.
- Keep explanations concise and decision-first.

## Engineering Priorities

1. Correctness first.
2. Maintainability second.
3. Speed third.

When tradeoffs are needed, prefer readable, predictable solutions.

## Safety Defaults

- Never commit or expose secrets, tokens, or credential files.
- Avoid destructive commands unless explicitly requested.
- Call out risky changes (schema, auth, permissions, deletion) before applying them.
- Preserve existing user changes; do not revert unrelated modifications.

## Code Quality Baseline

- Keep functions focused and names explicit.
- Avoid duplicated logic when a shared helper is appropriate.
- Handle errors intentionally; avoid silent failures.
- Match existing project style unless a clear local standard exists.

## Backend Defaults (General)

- Keep handlers/controllers thin.
- Move business logic into service-level modules.
- Validate input/output with explicit schemas.
- Enforce auth/ownership checks at shared boundaries.

## Frontend Defaults (General)

- Keep API logic in service/client modules.
- Model API payloads with explicit types.
- Ensure loading, error, empty, and success states are represented.
- Keep route protection explicit for auth/role flows.

## Testing Defaults

- Add tests for changed behavior, not just happy paths.
- Include at least one negative/edge case for important flows.
- Favor deterministic tests over brittle timing-dependent tests.

## Communication Defaults

- Summarize what changed, why it changed, and how it was verified.
- If verification is incomplete, say exactly what remains.
- Offer clear next steps rather than open-ended suggestions.