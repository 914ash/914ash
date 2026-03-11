# Quality Score

Use this rubric to quantify technical quality and track entropy.

Scoring scale per category: `0` (unacceptable) to `5` (excellent).

## Categories
1. Reliability: correctness, deterministic behavior, failure handling.
2. Security: authn/authz, input validation, secret handling, least privilege.
3. Observability: logs/metrics/traces, diagnosability, alertability.
4. Maintainability: readability, modularity, testability, docs freshness.
5. Operability: deploy safety, rollback path, runbook clarity.

## Current Baseline
- Reliability: 3
- Security: 2
- Observability: 1
- Maintainability: 3
- Operability: 1
- Total: 10/25

## Rules
- Re-score after major changes or incidents.
- Any category below `2` blocks "done" status for critical-path work.
- Link score changes to concrete evidence (tests, dashboards, docs, or code diffs).

## 2026-03-11 update
- Reliability increased to `3` due to explicit boundary validation and unit-test coverage in `demo_project`.
- Maintainability increased to `3` due to added runnable demo docs and deterministic module structure.
