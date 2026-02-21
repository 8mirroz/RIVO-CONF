# Orchestration Checklists

## 1. Task Decomposition Template
- Domain:
- Owner:
- Inputs:
- Outputs:
- Contracts touched:
- Blocking dependencies:
- Done criteria:

## 2. Merge Batch Template
- Batch ID:
- Included PRs:
- Shared contracts changed:
- Required checks:
- Rollback plan:

## 3. Dependency Ordering Rule
1. Schema/contract PR
2. Producer implementation PR
3. Consumer implementation PR
4. Integration and replay tests

## 4. Escalation Conditions
- Two or more domains edit same contract in parallel.
- Contract compatibility uncertainty.
- Replay tests become non-deterministic.
- Pricing/validation behavior differs between UI and API results.
