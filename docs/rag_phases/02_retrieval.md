# Phase 2: Retrieval (High-Recall Candidate Evidence Search)

## 0. Document Control
- Audience: platform, ML, product, compliance, and operations teams.
- Purpose: production-grade, theory-first specification for this phase.
- Upstream dependency: Indexed dense and sparse stores with rich metadata.
- Downstream dependency: Reranking precision and final answer grounding quality.
- Optimization target: maximize recall at K with bounded latency and cost.
- Primary risk: missing key evidence or surfacing stale and irrelevant evidence.
- Maturity requirement: deterministic outputs with rollback readiness.

## 1. Objectives and Formal Framing
- Business objective: return plausible evidence fast and consistently across intents.
- Technical objective: blend query understanding, dense retrieval, sparse retrieval, and fusion.
- Reliability objective: fail safe under ambiguity and degraded dependency states.
- Safety objective: prevent policy, privacy, and compliance violations.
- Mathematical framing: maximize utility U = quality - alpha*latency - beta*cost - gamma*risk.
- Governance framing: all non-default changes require owner, rationale, and rollback plan.

## 2. Data Contract
### 2.1 Inputs
1. User query and optional conversation context.
2. Routing hints such as domain and jurisdiction.
3. Query rewrite policy and limits.
4. Dense vector index and lexical index handles.
5. Metadata filters including temporal constraints.
6. Access-control context and tenant boundaries.
7. Top-K and fusion policy parameters.
8. Cache and timeout configuration.

### 2.2 Outputs
1. Top-K candidate chunks with fused rank features.
2. Per-retriever scoring traces.
3. Filter and rewrite decision logs.
4. Latency breakdown by retrieval stage.
5. Low-recall risk indicators.
6. Access-control enforcement outcomes.
7. Cache hit and miss metadata.
8. Reranker-ready candidate payload.

### 2.3 Contract Invariants
- Every output must include stable IDs and provenance metadata.
- Contract versions are explicit and tested in CI.
- Missing mandatory fields must trigger machine-readable errors.
- Contract violations must block unsafe promotion.

## 3. End-to-End Process Narrative
1. Validate incoming query request contract.
2. Classify intent and infer domain hints.
3. Extract entities and regulatory references.
4. Apply conservative rewrite expansions.
5. Embed query for semantic retrieval.
6. Execute dense nearest-neighbor search.
7. Execute sparse lexical search.
8. Apply metadata and temporal filters.
9. Merge and deduplicate candidate sets.
10. Fuse rankings with stable strategy.
11. Apply diversity balancing rules.
12. Measure score distribution confidence.
13. Detect and flag low-recall scenarios.
14. Emit retrieval diagnostics and traces.
15. Return selected candidates to reranker.
16. Update cache according to policy.
17. Record authorization decisions.
18. Monitor stage-level latency.
19. Persist request correlation metadata.
20. Close retrieval transaction safely.

## 4. Theoretical Foundations
### 4.1 Intent decomposition
- Definition: Intent decomposition determines reliability boundaries for this phase.
- Theory: model Intent decomposition as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Intent decomposition as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Intent decomposition.

### 4.2 Entity-aware query representation
- Definition: Entity-aware query representation determines reliability boundaries for this phase.
- Theory: model Entity-aware query representation as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Entity-aware query representation as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Entity-aware query representation.

### 4.3 Rewrite drift prevention
- Definition: Rewrite drift prevention determines reliability boundaries for this phase.
- Theory: model Rewrite drift prevention as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Rewrite drift prevention as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Rewrite drift prevention.

### 4.4 Semantic vector retrieval
- Definition: Semantic vector retrieval determines reliability boundaries for this phase.
- Theory: model Semantic vector retrieval as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Semantic vector retrieval as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Semantic vector retrieval.

### 4.5 Lexical BM25-style retrieval
- Definition: Lexical BM25-style retrieval determines reliability boundaries for this phase.
- Theory: model Lexical BM25-style retrieval as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Lexical BM25-style retrieval as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Lexical BM25-style retrieval.

### 4.6 Hybrid rank fusion
- Definition: Hybrid rank fusion determines reliability boundaries for this phase.
- Theory: model Hybrid rank fusion as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Hybrid rank fusion as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Hybrid rank fusion.

### 4.7 Score normalization discipline
- Definition: Score normalization discipline determines reliability boundaries for this phase.
- Theory: model Score normalization discipline as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Score normalization discipline as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Score normalization discipline.

### 4.8 Metadata filter correctness
- Definition: Metadata filter correctness determines reliability boundaries for this phase.
- Theory: model Metadata filter correctness as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Metadata filter correctness as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Metadata filter correctness.

### 4.9 Temporal retrieval validity
- Definition: Temporal retrieval validity determines reliability boundaries for this phase.
- Theory: model Temporal retrieval validity as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Temporal retrieval validity as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Temporal retrieval validity.

### 4.10 Source diversity balancing
- Definition: Source diversity balancing determines reliability boundaries for this phase.
- Theory: model Source diversity balancing as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Source diversity balancing as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Source diversity balancing.

### 4.11 Recall-latency tradeoff control
- Definition: Recall-latency tradeoff control determines reliability boundaries for this phase.
- Theory: model Recall-latency tradeoff control as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Recall-latency tradeoff control as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Recall-latency tradeoff control.

### 4.12 Cache consistency strategy
- Definition: Cache consistency strategy determines reliability boundaries for this phase.
- Theory: model Cache consistency strategy as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Cache consistency strategy as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Cache consistency strategy.

## 5. Production Controls
### 5.1 Query schema validation
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.2 Rewrite budget cap
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.3 Retriever timeout guard
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.4 Jurisdiction filter enforcement
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.5 Temporal validity filter gate
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.6 Access-control filter gate
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.7 Fusion stability check
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.8 Duplicate suppression check
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.9 Low-confidence retrieval flag
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.10 Fallback retrieval path
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.11 Latency circuit breaker
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.12 Trace completeness control
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

## 6. Failure Modes and Recovery
### 6.1 Intent drift from rewriting
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.2 Exact-citation miss in dense path
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.3 Semantic miss in sparse path
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.4 Over-filtering of valid evidence
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.5 Under-filtering of stale evidence
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.6 Fusion instability
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.7 Duplicate-heavy candidate list
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.8 Retriever timeout
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.9 Stale cache serving old results
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.10 Access-control misconfiguration
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.11 Latency spikes under burst load
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.12 Long-tail terminology miss
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

## 7. Metrics and SLOs
### 7.1 Recall at K
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.2 MRR
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.3 nDCG
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.4 Rewrite acceptance rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.5 Filter precision
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.6 Temporal correctness rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.7 Source diversity index
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.8 Retriever timeout rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.9 P50 latency
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.10 P95 latency
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.11 Cache hit ratio
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.12 Unauthorized retrieval block rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

## 8. Validation and Testing
### 8.1 Dense relevance regression
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.2 Sparse relevance regression
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.3 Fusion ranking stability tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.4 Rewrite adversarial tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.5 Filter correctness tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.6 Temporal retrieval tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.7 Duplicate suppression tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.8 Fallback path tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.9 Burst latency tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.10 Cache coherence tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.11 Authorization boundary tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.12 End-to-end recall gate tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

## 9. Deployment and Operations
### 9.1 Top-K tuning based on recall and latency
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.2 Fusion calibration with labeled data
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.3 Low-recall incident review
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.4 Query rewrite audit with SMEs
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.5 Temporal filter audits
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.6 Cache policy review
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.7 Retriever failover drill
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.8 Access-control audit after policy updates
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.9 KPI reporting cadence
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.10 Canary rollout for retrieval changes
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.11 Rollback playbook execution
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.12 Runbook revision after incidents
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

## 10. Production Readiness Checklist
- [1] Recall target achieved on benchmark.
- [2] Hybrid retrieval calibrated.
- [3] Rewrite policy constrained and logged.
- [4] Temporal filters validated.
- [5] Access controls verified.
- [6] Duplicate suppression effective.
- [7] Latency SLO satisfied.
- [8] Fallback behavior tested.
- [9] Cache invalidation reliable.
- [10] Diagnostics complete.
- [11] Regression gates active.
- [12] On-call procedures updated.
- [final] Promote only if mandatory controls and quality gates are green.

## 11. Integration and Governance Notes
- Validate this phase in isolation and in full pipeline integration tests.
- Include temporal and jurisdiction-sensitive scenarios in all acceptance suites.
- Run capacity drills for burst traffic and long-tail query distributions.
- Retain signed evaluation and deployment artifacts for audits.
- Review this document after every major incident or architecture change.

