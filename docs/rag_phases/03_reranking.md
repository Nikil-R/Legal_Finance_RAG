# Phase 3: Reranking (Precision-First Evidence Curation)

## 0. Document Control
- Audience: platform, ML, product, compliance, and operations teams.
- Purpose: production-grade, theory-first specification for this phase.
- Upstream dependency: Hybrid retrieval candidates and retrieval diagnostics.
- Downstream dependency: Context builder quality and generation faithfulness.
- Optimization target: maximize precision at N while preserving evidence coverage.
- Primary risk: noisy context or omission of decisive evidence.
- Maturity requirement: deterministic outputs with rollback readiness.

## 1. Objectives and Formal Framing
- Business objective: promote evidence that directly supports trustworthy answers.
- Technical objective: score query-document pairs with high-fidelity relevance models and policies.
- Reliability objective: fail safe under ambiguity and degraded dependency states.
- Safety objective: prevent policy, privacy, and compliance violations.
- Mathematical framing: maximize utility U = quality - alpha*latency - beta*cost - gamma*risk.
- Governance framing: all non-default changes require owner, rationale, and rollback plan.

## 2. Data Contract
### 2.1 Inputs
1. Normalized query representation.
2. Top-K retrieved candidates with metadata.
3. Reranker model and threshold configuration.
4. Diversity constraints and deduplication policy.
5. Latency budget for scoring.
6. Abstention policy thresholds.
7. Token budget hints for downstream context.
8. Trace correlation identifiers.

### 2.2 Outputs
1. Top-N reranked evidence with calibrated scores.
2. Discarded candidate reasons.
3. Abstention signal when confidence is low.
4. Diversity and redundancy metrics.
5. Latency and inference diagnostics.
6. Score distribution metadata.
7. Trace linkage to retrieval stage.
8. Context-ready evidence payload.

### 2.3 Contract Invariants
- Every output must include stable IDs and provenance metadata.
- Contract versions are explicit and tested in CI.
- Missing mandatory fields must trigger machine-readable errors.
- Contract violations must block unsafe promotion.

## 3. End-to-End Process Narrative
1. Validate candidate payload schema.
2. Generate query-document scoring pairs.
3. Run pairwise relevance model.
4. Normalize and calibrate score outputs.
5. Sort candidates by calibrated relevance.
6. Apply minimum confidence threshold.
7. Enforce diversity constraints.
8. Remove near-duplicate evidence chunks.
9. Apply token-budget aware selection.
10. Select top-N evidence set.
11. Compute reranking confidence summary.
12. Emit abstention recommendation when needed.
13. Persist full scoring trace for analysis.
14. Monitor latency and model errors.
15. Return curated evidence to context builder.
16. Record configuration fingerprints.
17. Cache deterministic outputs where safe.
18. Route anomalies to incident channel.
19. Update observability stream.
20. Close reranking transaction.

## 4. Theoretical Foundations
### 4.1 Pairwise semantic relevance
- Definition: Pairwise semantic relevance determines reliability boundaries for this phase.
- Theory: model Pairwise semantic relevance as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Pairwise semantic relevance as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Pairwise semantic relevance.

### 4.2 Cross-encoder precision benefits
- Definition: Cross-encoder precision benefits determines reliability boundaries for this phase.
- Theory: model Cross-encoder precision benefits as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Cross-encoder precision benefits as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Cross-encoder precision benefits.

### 4.3 Score calibration and comparability
- Definition: Score calibration and comparability determines reliability boundaries for this phase.
- Theory: model Score calibration and comparability as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Score calibration and comparability as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Score calibration and comparability.

### 4.4 Threshold-based abstention
- Definition: Threshold-based abstention determines reliability boundaries for this phase.
- Theory: model Threshold-based abstention as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Threshold-based abstention as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Threshold-based abstention.

### 4.5 Diversity-aware selection
- Definition: Diversity-aware selection determines reliability boundaries for this phase.
- Theory: model Diversity-aware selection as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Diversity-aware selection as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Diversity-aware selection.

### 4.6 Redundancy suppression
- Definition: Redundancy suppression determines reliability boundaries for this phase.
- Theory: model Redundancy suppression as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Redundancy suppression as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Redundancy suppression.

### 4.7 Token-budget optimization
- Definition: Token-budget optimization determines reliability boundaries for this phase.
- Theory: model Token-budget optimization as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Token-budget optimization as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Token-budget optimization.

### 4.8 Latency-constrained inference
- Definition: Latency-constrained inference determines reliability boundaries for this phase.
- Theory: model Latency-constrained inference as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Latency-constrained inference as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Latency-constrained inference.

### 4.9 Confidence signal reliability
- Definition: Confidence signal reliability determines reliability boundaries for this phase.
- Theory: model Confidence signal reliability as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Confidence signal reliability as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Confidence signal reliability.

### 4.10 Ranking stability analysis
- Definition: Ranking stability analysis determines reliability boundaries for this phase.
- Theory: model Ranking stability analysis as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Ranking stability analysis as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Ranking stability analysis.

### 4.11 Domain-specific relevance behavior
- Definition: Domain-specific relevance behavior determines reliability boundaries for this phase.
- Theory: model Domain-specific relevance behavior as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Domain-specific relevance behavior as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Domain-specific relevance behavior.

### 4.12 Offline-online alignment
- Definition: Offline-online alignment determines reliability boundaries for this phase.
- Theory: model Offline-online alignment as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Offline-online alignment as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Offline-online alignment.

## 5. Production Controls
### 5.1 Candidate schema gate
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.2 Inference timeout and fallback
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.3 Score normalization guard
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.4 Threshold governance
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.5 Diversity enforcement
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.6 Duplicate suppression gate
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.7 Top-N boundary check
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.8 Abstention trigger policy
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.9 Model version lock
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.10 Trace logging guarantee
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.11 Latency SLO monitor
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.12 Canary release control
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

## 6. Failure Modes and Recovery
### 6.1 Overfitted relevance scoring
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.2 Threshold too strict
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.3 Threshold too loose
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.4 Redundant evidence dominance
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.5 Missing key minority evidence
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.6 Latency spikes for large K
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.7 Inference service degradation
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.8 Unstable tie-breaking behavior
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.9 Confidence score misuse downstream
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.10 Token truncation of key evidence
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.11 Unobserved regression after model update
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.12 Insufficient traceability for audits
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

## 7. Metrics and SLOs
### 7.1 Precision at N
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.2 Top-1 relevance accuracy
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.3 Abstention recommendation rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.4 False-negative relevance rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.5 Diversity index in top-N
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.6 Duplicate suppression ratio
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.7 P50 reranking latency
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.8 P95 reranking latency
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.9 Inference error rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.10 Score stability score
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.11 Handoff quality to generation
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.12 Canary delta versus baseline
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

## 8. Validation and Testing
### 8.1 Pairwise relevance regression
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.2 Threshold calibration tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.3 Diversity constraint tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.4 Near-duplicate suppression tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.5 Latency scaling tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.6 Model compatibility tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.7 Deterministic tie-break tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.8 Fallback behavior tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.9 Confidence contract tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.10 Token-budget truncation tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.11 Canary gating tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.12 End-to-end faithfulness impact tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

## 9. Deployment and Operations
### 9.1 Monthly threshold recalibration
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.2 Abstention case reviews with SMEs
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.3 Candidate size tuning
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.4 Reranker drift monitoring
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.5 Duplicate-pattern audits
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.6 Deterministic replay for incidents
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.7 Rollback package maintenance
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.8 KPI reporting
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.9 Canary rollout execution
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.10 Diversity policy patching
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.11 Runbook updates after postmortems
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.12 Cross-team retrieval-reranking alignment
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

## 10. Production Readiness Checklist
- [1] Reranker version pinned.
- [2] Thresholds calibrated and approved.
- [3] Top-N aligned with context budget.
- [4] Diversity controls validated.
- [5] Duplicate suppression validated.
- [6] Latency SLO met.
- [7] Abstention policy tested.
- [8] Fallback path verified.
- [9] Traceability complete.
- [10] Canary process enforced.
- [11] Regression suite passing.
- [12] On-call playbook current.
- [final] Promote only if mandatory controls and quality gates are green.

## 11. Integration and Governance Notes
- Validate this phase in isolation and in full pipeline integration tests.
- Include temporal and jurisdiction-sensitive scenarios in all acceptance suites.
- Run capacity drills for burst traffic and long-tail query distributions.
- Retain signed evaluation and deployment artifacts for audits.
- Review this document after every major incident or architecture change.

