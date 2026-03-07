# Phase 5: Evaluation and Continuous Improvement (Release-Quality Governance)

## 0. Document Control
- Audience: platform, ML, product, compliance, and operations teams.
- Purpose: production-grade, theory-first specification for this phase.
- Upstream dependency: Artifacts from all prior phases, including traces and outputs.
- Downstream dependency: Release decisions, remediation backlog, and iterative quality improvements.
- Optimization target: maximize reliable quality and detect regressions before user impact.
- Primary risk: silent quality degradation and non-compliant behavior in production.
- Maturity requirement: deterministic outputs with rollback readiness.

## 1. Objectives and Formal Framing
- Business objective: establish objective, reproducible quality governance for RAG releases.
- Technical objective: evaluate component and end-to-end behavior with robust metrics and gates.
- Reliability objective: fail safe under ambiguity and degraded dependency states.
- Safety objective: prevent policy, privacy, and compliance violations.
- Mathematical framing: maximize utility U = quality - alpha*latency - beta*cost - gamma*risk.
- Governance framing: all non-default changes require owner, rationale, and rollback plan.

## 2. Data Contract
### 2.1 Inputs
1. Golden dataset with questions and expected evidence.
2. Pipeline traces from retrieval, reranking, and generation.
3. Metric definitions and scoring rubrics.
4. Judge-model settings and calibration references.
5. Historical baseline metrics and thresholds.
6. Domain and difficulty segmentation maps.
7. Operational telemetry for latency and cost.
8. Incident and user-feedback data.

### 2.2 Outputs
1. Component and end-to-end evaluation reports.
2. Pass/fail release-gate decisions.
3. Regression diffs against baseline.
4. Failure taxonomy and root-cause hints.
5. Prioritized remediation action list.
6. Updated benchmark candidates from failures.
7. Governance-ready audit package.
8. Continuous-improvement execution plan.

### 2.3 Contract Invariants
- Every output must include stable IDs and provenance metadata.
- Contract versions are explicit and tested in CI.
- Missing mandatory fields must trigger machine-readable errors.
- Contract violations must block unsafe promotion.

## 3. End-to-End Process Narrative
1. Validate benchmark and rubric integrity.
2. Run fixed-config pipeline on benchmark suite.
3. Score retrieval quality metrics.
4. Score reranking quality metrics.
5. Score generation faithfulness and correctness.
6. Validate citations and policy compliance.
7. Aggregate metrics by segment and domain.
8. Compare against baseline and control cohorts.
9. Apply release gate thresholds.
10. Classify failures by root-cause layer.
11. Attach latency and cost trend analysis.
12. Generate stakeholder-facing reports.
13. Block release on critical regressions.
14. Promote only if all mandatory checks pass.
15. Store reproducibility artifacts and signatures.
16. Feed real production failures into benchmark queue.
17. Calibrate judge-model consistency periodically.
18. Run human SME arbitration on disputed cases.
19. Assign remediation tasks with owners.
20. Close cycle with updated baseline and action log.

## 4. Theoretical Foundations
### 4.1 Component versus end-to-end evaluation
- Definition: Component versus end-to-end evaluation determines reliability boundaries for this phase.
- Theory: model Component versus end-to-end evaluation as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Component versus end-to-end evaluation as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Component versus end-to-end evaluation.

### 4.2 Benchmark representativeness
- Definition: Benchmark representativeness determines reliability boundaries for this phase.
- Theory: model Benchmark representativeness as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Benchmark representativeness as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Benchmark representativeness.

### 4.3 Faithfulness versus correctness separation
- Definition: Faithfulness versus correctness separation determines reliability boundaries for this phase.
- Theory: model Faithfulness versus correctness separation as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Faithfulness versus correctness separation as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Faithfulness versus correctness separation.

### 4.4 Retrieval ranking metric interpretation
- Definition: Retrieval ranking metric interpretation determines reliability boundaries for this phase.
- Theory: model Retrieval ranking metric interpretation as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Retrieval ranking metric interpretation as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Retrieval ranking metric interpretation.

### 4.5 Citation quality as trust metric
- Definition: Citation quality as trust metric determines reliability boundaries for this phase.
- Theory: model Citation quality as trust metric as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Citation quality as trust metric as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Citation quality as trust metric.

### 4.6 Judge-model calibration
- Definition: Judge-model calibration determines reliability boundaries for this phase.
- Theory: model Judge-model calibration as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Judge-model calibration as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Judge-model calibration.

### 4.7 Segment-level fairness analysis
- Definition: Segment-level fairness analysis determines reliability boundaries for this phase.
- Theory: model Segment-level fairness analysis as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Segment-level fairness analysis as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Segment-level fairness analysis.

### 4.8 Regression gate governance
- Definition: Regression gate governance determines reliability boundaries for this phase.
- Theory: model Regression gate governance as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Regression gate governance as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Regression gate governance.

### 4.9 Error taxonomy discipline
- Definition: Error taxonomy discipline determines reliability boundaries for this phase.
- Theory: model Error taxonomy discipline as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Error taxonomy discipline as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Error taxonomy discipline.

### 4.10 Cost-quality-latency balancing
- Definition: Cost-quality-latency balancing determines reliability boundaries for this phase.
- Theory: model Cost-quality-latency balancing as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Cost-quality-latency balancing as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Cost-quality-latency balancing.

### 4.11 Temporal drift detection
- Definition: Temporal drift detection determines reliability boundaries for this phase.
- Theory: model Temporal drift detection as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Temporal drift detection as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Temporal drift detection.

### 4.12 Closed-loop improvement design
- Definition: Closed-loop improvement design determines reliability boundaries for this phase.
- Theory: model Closed-loop improvement design as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Closed-loop improvement design as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Closed-loop improvement design.

## 5. Production Controls
### 5.1 Benchmark version lock
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.2 Reproducibility contract enforcement
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.3 Automated release-gate blocker
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.4 Rubric version control
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.5 Human review for high-impact failures
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.6 Metric integrity validation
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.7 Segment reporting requirement
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.8 Significance-check control
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.9 Incident-triggered re-evaluation
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.10 Report archival policy
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.11 Environment parity checks
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.12 Post-release backtest requirement
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

## 6. Failure Modes and Recovery
### 6.1 Benchmark overfitting
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.2 Data leakage into evaluation
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.3 Judge inconsistency
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.4 Aggregate masking of segment regressions
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.5 Disabled release gate
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.6 Faithfulness false positives
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.7 Ignored latency regressions
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.8 Missing policy scenarios in tests
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.9 Untriaged recurring failures
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.10 Release despite red metrics
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.11 Drift after corpus updates
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.12 Insufficient decision audit trail
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

## 7. Metrics and SLOs
### 7.1 Faithfulness
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.2 Answer correctness
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.3 Retrieval recall at K
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.4 Reranking precision at N
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.5 Citation validity
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.6 Policy compliance rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.7 Segment parity gap
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.8 P95 latency
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.9 Cost per request
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.10 Release regression count
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.11 Post-release incident rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.12 Benchmark freshness score
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

## 8. Validation and Testing
### 8.1 Benchmark leakage tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.2 Reproducibility tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.3 Metric unit tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.4 Judge consistency tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.5 Segment fairness tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.6 Release-gate simulation tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.7 Root-cause classification tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.8 Latency trend tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.9 Policy compliance tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.10 Ablation impact tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.11 Canary-vs-baseline tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.12 Post-release backtests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

## 9. Deployment and Operations
### 9.1 Nightly benchmark evaluation
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.2 Pre-release full gate run
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.3 Domain regression review meetings
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.4 Benchmark refresh workflow
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.5 Quarterly judge calibration
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.6 Monthly quality and compliance report
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.7 Remediation backlog tracking
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.8 Emergency re-evaluation protocol
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.9 Signed artifact retention
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.10 Release go/no-go governance
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.11 Threshold updates by risk profile
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.12 On-call diagnostics training
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

## 10. Production Readiness Checklist
- [1] Benchmark representative and versioned.
- [2] Runs reproducible and auditable.
- [3] Mandatory metrics computed.
- [4] Release gates enforced automatically.
- [5] Judge calibration monitored.
- [6] Human review path active.
- [7] Failure taxonomy actionable.
- [8] Latency and cost tracked with quality.
- [9] Policy compliance included in pass criteria.
- [10] Production failures fed back to benchmarks.
- [11] Audit artifacts retained.
- [12] Continuous improvement loop operating.
- [final] Promote only if mandatory controls and quality gates are green.

## 11. Integration and Governance Notes
- Validate this phase in isolation and in full pipeline integration tests.
- Include temporal and jurisdiction-sensitive scenarios in all acceptance suites.
- Run capacity drills for burst traffic and long-tail query distributions.
- Retain signed evaluation and deployment artifacts for audits.
- Review this document after every major incident or architecture change.

