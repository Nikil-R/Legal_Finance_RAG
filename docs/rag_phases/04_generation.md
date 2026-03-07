# Phase 4: Generation and Guardrails (Grounded Answer Delivery)

## 0. Document Control
- Audience: platform, ML, product, compliance, and operations teams.
- Purpose: production-grade, theory-first specification for this phase.
- Upstream dependency: Curated evidence and confidence metadata from reranking.
- Downstream dependency: User-facing response quality, compliance posture, and trust outcomes.
- Optimization target: maximize grounded usefulness with minimal hallucination and policy risk.
- Primary risk: unsupported claims, citation errors, or unsafe responses.
- Maturity requirement: deterministic outputs with rollback readiness.

## 1. Objectives and Formal Framing
- Business objective: deliver clear answers that are verifiable, compliant, and useful.
- Technical objective: control prompting, decoding, citation, and validation as one pipeline.
- Reliability objective: fail safe under ambiguity and degraded dependency states.
- Safety objective: prevent policy, privacy, and compliance violations.
- Mathematical framing: maximize utility U = quality - alpha*latency - beta*cost - gamma*risk.
- Governance framing: all non-default changes require owner, rationale, and rollback plan.

## 2. Data Contract
### 2.1 Inputs
1. User question and context window.
2. Reranked evidence blocks with source IDs.
3. System prompt policy and response schema.
4. Decoding and token budget parameters.
5. Safety policy and refusal rules.
6. Disclaimer and legal boundary policy.
7. Citation validator and claim checker configs.
8. Audit and logging context.

### 2.2 Outputs
1. Grounded answer text.
2. Citation map linking claims to evidence IDs.
3. Abstention or refusal when required.
4. Safety intervention indicators.
5. Validation and repair report.
6. Latency and token usage telemetry.
7. Signed trace metadata for audit.
8. Final response payload for clients.

### 2.3 Contract Invariants
- Every output must include stable IDs and provenance metadata.
- Contract versions are explicit and tested in CI.
- Missing mandatory fields must trigger machine-readable errors.
- Contract violations must block unsafe promotion.

## 3. End-to-End Process Narrative
1. Validate evidence package integrity.
2. Build constrained system prompt.
3. Inject evidence with stable citation IDs.
4. Apply deterministic decoding policy.
5. Generate first-pass answer draft.
6. Extract and validate citations.
7. Run unsupported-claim checks.
8. Run safety and policy filters.
9. Apply mandatory disclaimer policies.
10. Validate output schema and formatting.
11. Repair or refuse on validation failure.
12. Attach confidence and trace metadata.
13. Log prompt and response fingerprints.
14. Measure latency and token budgets.
15. Return validated response to client.
16. Route high-risk responses for review.
17. Record intervention outcomes.
18. Feed samples to evaluation pipeline.
19. Update guardrail dashboards.
20. Close response transaction with audit ID.

## 4. Theoretical Foundations
### 4.1 Grounded generation constraints
- Definition: Grounded generation constraints determines reliability boundaries for this phase.
- Theory: model Grounded generation constraints as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Grounded generation constraints as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Grounded generation constraints.

### 4.2 Instruction hierarchy control
- Definition: Instruction hierarchy control determines reliability boundaries for this phase.
- Theory: model Instruction hierarchy control as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Instruction hierarchy control as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Instruction hierarchy control.

### 4.3 Claim-level citation binding
- Definition: Claim-level citation binding determines reliability boundaries for this phase.
- Theory: model Claim-level citation binding as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Claim-level citation binding as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Claim-level citation binding.

### 4.4 Evidence sufficiency checks
- Definition: Evidence sufficiency checks determines reliability boundaries for this phase.
- Theory: model Evidence sufficiency checks as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Evidence sufficiency checks as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Evidence sufficiency checks.

### 4.5 Deterministic decoding strategy
- Definition: Deterministic decoding strategy determines reliability boundaries for this phase.
- Theory: model Deterministic decoding strategy as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Deterministic decoding strategy as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Deterministic decoding strategy.

### 4.6 Post-generation verification loop
- Definition: Post-generation verification loop determines reliability boundaries for this phase.
- Theory: model Post-generation verification loop as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Post-generation verification loop as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Post-generation verification loop.

### 4.7 Schema-constrained output
- Definition: Schema-constrained output determines reliability boundaries for this phase.
- Theory: model Schema-constrained output as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Schema-constrained output as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Schema-constrained output.

### 4.8 Safety policy layering
- Definition: Safety policy layering determines reliability boundaries for this phase.
- Theory: model Safety policy layering as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Safety policy layering as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Safety policy layering.

### 4.9 Regulatory disclaimer compliance
- Definition: Regulatory disclaimer compliance determines reliability boundaries for this phase.
- Theory: model Regulatory disclaimer compliance as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Regulatory disclaimer compliance as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Regulatory disclaimer compliance.

### 4.10 Citation hallucination prevention
- Definition: Citation hallucination prevention determines reliability boundaries for this phase.
- Theory: model Citation hallucination prevention as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Citation hallucination prevention as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Citation hallucination prevention.

### 4.11 Prompt injection resistance
- Definition: Prompt injection resistance determines reliability boundaries for this phase.
- Theory: model Prompt injection resistance as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Prompt injection resistance as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Prompt injection resistance.

### 4.12 Auditability by design
- Definition: Auditability by design determines reliability boundaries for this phase.
- Theory: model Auditability by design as a controlled variable in constrained optimization.
- Statistical perspective: monitor distribution shift, not only averages.
- Engineering implication: expose Auditability by design as explicit configuration with safe defaults.
- Failure signal: KPI drift after data, model, or config changes.
- Mitigation: canary rollout, guard thresholds, and rapid rollback.
- Governance: record owner and rationale for every non-default choice of Auditability by design.

## 5. Production Controls
### 5.1 System prompt grounding lock
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.2 Context size guard
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.3 Citation existence validator
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.4 Claim-evidence consistency checker
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.5 Safety gate
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.6 Disclaimer injector
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.7 Output schema validator
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.8 Abstention fallback control
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.9 Injection detection filter
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.10 Model/config version pinning
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.11 Sensitive output redaction
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

### 5.12 Trace retention policy
- Intent: prevent avoidable degradation and policy violations.
- Trigger: activate on threshold breach or invariant break.
- Enforcement: block, degrade gracefully, or abstain.
- Telemetry: emit before/after state with correlation IDs.
- Validation: verify with synthetic and replayed production traffic.
- Ownership: assign primary and secondary operational owners.

## 6. Failure Modes and Recovery
### 6.1 Unsupported but fluent claims
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.2 Invalid citation indices
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.3 Citation-claim mismatch
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.4 Prompt injection override
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.5 Safety false negatives
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.6 Over-refusal due to strict filters
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.7 Missing disclaimers
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.8 Schema violations in responses
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.9 Token truncation of qualifiers
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.10 Latency spikes with long context
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.11 Behavior drift after model change
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

### 6.12 Incomplete audit traces
- Detection: alerts, anomaly detection, and contract failures.
- User impact: quality loss, latency increase, or unsafe output behavior.
- Containment: isolate path, freeze rollout, and protect users first.
- Recovery: restore last known good configuration and replay samples.
- Long-term fix: add regression tests and update runbooks.
- Postmortem: document root cause, blast radius, and prevention tasks.

## 7. Metrics and SLOs
### 7.1 Faithfulness score
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.2 Citation validity rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.3 Unsupported claim rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.4 Refusal appropriateness rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.5 Safety intervention precision
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.6 Schema compliance rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.7 Disclaimer inclusion rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.8 P50 generation latency
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.9 P95 generation latency
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.10 Token efficiency
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.11 User-rated usefulness
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

### 7.12 Policy violation incident rate
- Definition: metric formula and time window are versioned.
- Thresholds: green, yellow, and red bands per environment.
- Segmentation: domain, intent class, data freshness, and traffic slice.
- Alerting: page only on sustained breach to reduce noise.
- Decision use: release gating, rollback triggers, and prioritization.

## 8. Validation and Testing
### 8.1 Grounding regression tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.2 Citation adversarial tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.3 Unsupported claim detection tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.4 Prompt injection tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.5 Safety policy tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.6 Disclaimer enforcement tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.7 Schema validation tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.8 Abstention path tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.9 Long-context latency tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.10 Determinism snapshot tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.11 Sensitive output tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

### 8.12 SME acceptance tests
- Objective: verify correctness, stability, and safety behavior.
- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.
- Pass criteria: deterministic thresholds tied to production risk.
- Automation: mandatory in CI with release block on regression.
- Traceability: store model version, config hash, and dataset snapshot.

## 9. Deployment and Operations
### 9.1 Unsupported-claim incident review
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.2 Refusal threshold calibration
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.3 Citation failure triage
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.4 Prompt template A/B governance
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.5 Red-team safety exercises
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.6 Disclaimer coverage audits
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.7 Token cost monitoring
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.8 Canary rollout for model changes
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.9 Fallback model readiness checks
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.10 Weekly quality dashboard publication
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.11 Quarterly compliance audit
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

### 9.12 Runbook improvement loop
- Pre-check: validate dependencies, credentials, and schema compatibility.
- Execution: run controlled stage deployment before full rollout.
- Health check: verify top KPIs and error budget immediately.
- Rollback: revert on sustained threshold breach or policy violation.
- Audit: retain logs, decision records, and timeline artifacts.

## 10. Production Readiness Checklist
- [1] Grounding rules enforced.
- [2] Citation validation blocking invalid outputs.
- [3] Claim checks operational.
- [4] Safety gates validated.
- [5] Disclaimer compliance guaranteed.
- [6] Schema validation enabled.
- [7] Abstention behavior tested.
- [8] Latency budget met.
- [9] Injection resilience verified.
- [10] Trace artifacts retained.
- [11] Canary rollout required.
- [12] Incident response ready.
- [final] Promote only if mandatory controls and quality gates are green.

## 11. Integration and Governance Notes
- Validate this phase in isolation and in full pipeline integration tests.
- Include temporal and jurisdiction-sensitive scenarios in all acceptance suites.
- Run capacity drills for burst traffic and long-tail query distributions.
- Retain signed evaluation and deployment artifacts for audits.
- Review this document after every major incident or architecture change.

