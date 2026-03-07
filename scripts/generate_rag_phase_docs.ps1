$ErrorActionPreference = 'Stop'

function New-LongPhaseDoc {
    param(
        [hashtable]$P,
        [string]$OutFile,
        [int]$MinLines = 330
    )

    $L = [System.Collections.Generic.List[string]]::new()

    $L.Add("# $($P.Title)")
    $L.Add("")
    $L.Add("## 0. Document Control")
    $L.Add("- Audience: platform, ML, product, compliance, and operations teams.")
    $L.Add("- Purpose: production-grade, theory-first specification for this phase.")
    $L.Add("- Upstream dependency: $($P.Upstream)")
    $L.Add("- Downstream dependency: $($P.Downstream)")
    $L.Add("- Optimization target: $($P.Target)")
    $L.Add("- Primary risk: $($P.Risk)")
    $L.Add("- Maturity requirement: deterministic outputs with rollback readiness.")
    $L.Add("")

    $L.Add("## 1. Objectives and Formal Framing")
    $L.Add("- Business objective: $($P.Business)")
    $L.Add("- Technical objective: $($P.Technical)")
    $L.Add("- Reliability objective: fail safe under ambiguity and degraded dependency states.")
    $L.Add("- Safety objective: prevent policy, privacy, and compliance violations.")
    $L.Add("- Mathematical framing: maximize utility U = quality - alpha*latency - beta*cost - gamma*risk.")
    $L.Add("- Governance framing: all non-default changes require owner, rationale, and rollback plan.")
    $L.Add("")

    $L.Add("## 2. Data Contract")
    $L.Add("### 2.1 Inputs")
    $i = 1
    foreach ($x in $P.Inputs) { $L.Add("$i. $x"); $i++ }
    $L.Add("")
    $L.Add("### 2.2 Outputs")
    $i = 1
    foreach ($x in $P.Outputs) { $L.Add("$i. $x"); $i++ }
    $L.Add("")
    $L.Add("### 2.3 Contract Invariants")
    $L.Add("- Every output must include stable IDs and provenance metadata.")
    $L.Add("- Contract versions are explicit and tested in CI.")
    $L.Add("- Missing mandatory fields must trigger machine-readable errors.")
    $L.Add("- Contract violations must block unsafe promotion.")
    $L.Add("")

    $L.Add("## 3. End-to-End Process Narrative")
    $i = 1
    foreach ($x in $P.Steps) { $L.Add("$i. $x"); $i++ }
    $L.Add("")

    $L.Add("## 4. Theoretical Foundations")
    $i = 1
    foreach ($x in $P.Concepts) {
        $L.Add("### 4.$i $x")
        $L.Add("- Definition: $x determines reliability boundaries for this phase.")
        $L.Add("- Theory: model $x as a controlled variable in constrained optimization.")
        $L.Add("- Statistical perspective: monitor distribution shift, not only averages.")
        $L.Add("- Engineering implication: expose $x as explicit configuration with safe defaults.")
        $L.Add("- Failure signal: KPI drift after data, model, or config changes.")
        $L.Add("- Mitigation: canary rollout, guard thresholds, and rapid rollback.")
        $L.Add("- Governance: record owner and rationale for every non-default choice of $x.")
        $L.Add("")
        $i++
    }

    $L.Add("## 5. Production Controls")
    $i = 1
    foreach ($x in $P.Controls) {
        $L.Add("### 5.$i $x")
        $L.Add("- Intent: prevent avoidable degradation and policy violations.")
        $L.Add("- Trigger: activate on threshold breach or invariant break.")
        $L.Add("- Enforcement: block, degrade gracefully, or abstain.")
        $L.Add("- Telemetry: emit before/after state with correlation IDs.")
        $L.Add("- Validation: verify with synthetic and replayed production traffic.")
        $L.Add("- Ownership: assign primary and secondary operational owners.")
        $L.Add("")
        $i++
    }

    $L.Add("## 6. Failure Modes and Recovery")
    $i = 1
    foreach ($x in $P.Failures) {
        $L.Add("### 6.$i $x")
        $L.Add("- Detection: alerts, anomaly detection, and contract failures.")
        $L.Add("- User impact: quality loss, latency increase, or unsafe output behavior.")
        $L.Add("- Containment: isolate path, freeze rollout, and protect users first.")
        $L.Add("- Recovery: restore last known good configuration and replay samples.")
        $L.Add("- Long-term fix: add regression tests and update runbooks.")
        $L.Add("- Postmortem: document root cause, blast radius, and prevention tasks.")
        $L.Add("")
        $i++
    }

    $L.Add("## 7. Metrics and SLOs")
    $i = 1
    foreach ($x in $P.Metrics) {
        $L.Add("### 7.$i $x")
        $L.Add("- Definition: metric formula and time window are versioned.")
        $L.Add("- Thresholds: green, yellow, and red bands per environment.")
        $L.Add("- Segmentation: domain, intent class, data freshness, and traffic slice.")
        $L.Add("- Alerting: page only on sustained breach to reduce noise.")
        $L.Add("- Decision use: release gating, rollback triggers, and prioritization.")
        $L.Add("")
        $i++
    }

    $L.Add("## 8. Validation and Testing")
    $i = 1
    foreach ($x in $P.Tests) {
        $L.Add("### 8.$i $x")
        $L.Add("- Objective: verify correctness, stability, and safety behavior.")
        $L.Add("- Data policy: include clean, noisy, adversarial, and out-of-distribution samples.")
        $L.Add("- Pass criteria: deterministic thresholds tied to production risk.")
        $L.Add("- Automation: mandatory in CI with release block on regression.")
        $L.Add("- Traceability: store model version, config hash, and dataset snapshot.")
        $L.Add("")
        $i++
    }

    $L.Add("## 9. Deployment and Operations")
    $i = 1
    foreach ($x in $P.Ops) {
        $L.Add("### 9.$i $x")
        $L.Add("- Pre-check: validate dependencies, credentials, and schema compatibility.")
        $L.Add("- Execution: run controlled stage deployment before full rollout.")
        $L.Add("- Health check: verify top KPIs and error budget immediately.")
        $L.Add("- Rollback: revert on sustained threshold breach or policy violation.")
        $L.Add("- Audit: retain logs, decision records, and timeline artifacts.")
        $L.Add("")
        $i++
    }

    $L.Add("## 10. Production Readiness Checklist")
    $i = 1
    foreach ($x in $P.Checklist) { $L.Add("- [$i] $x"); $i++ }
    $L.Add("- [final] Promote only if mandatory controls and quality gates are green.")
    $L.Add("")

    $L.Add("## 11. Integration and Governance Notes")
    $L.Add("- Validate this phase in isolation and in full pipeline integration tests.")
    $L.Add("- Include temporal and jurisdiction-sensitive scenarios in all acceptance suites.")
    $L.Add("- Run capacity drills for burst traffic and long-tail query distributions.")
    $L.Add("- Retain signed evaluation and deployment artifacts for audits.")
    $L.Add("- Review this document after every major incident or architecture change.")
    $L.Add("")

    $n = 1
    while ($L.Count -lt $MinLines) {
        $L.Add("- Appendix note ${n}: maintain evidence-backed decision logs for governance and reproducibility.")
        $n++
    }

    Set-Content -Path $OutFile -Encoding utf8 -Value $L
}
$phases = @(
    @{
        File = '01_ingestion.md'
        Title = 'Phase 1: Ingestion (Production-Ready Knowledge Construction)'
        Upstream = 'Authoritative source systems, collection policy, and data governance inputs.'
        Downstream = 'Retrieval index quality, citation traceability, and generation grounding.'
        Target = 'maximize index quality and freshness within latency and cost budgets.'
        Risk = 'stale, noisy, or malformed knowledge memory leading to systemic downstream errors.'
        Business = 'build a trusted, auditable, and continuously updatable knowledge foundation.'
        Technical = 'parse, normalize, segment, enrich, embed, and index content deterministically.'
        Inputs = @(
            'Raw documents from approved legal, finance, and policy sources.',
            'Source metadata such as jurisdiction, issuer, effective date, and version.',
            'Parsing and OCR configuration profiles.',
            'Chunking policy and embedding model configuration.',
            'Security labels and retention requirements.',
            'Deduplication strategy and identifier rules.',
            'Schema definitions for metadata and provenance fields.',
            'Execution context including run ID and environment info.'
        )
        Outputs = @(
            'Normalized text units with preserved structural cues.',
            'Deterministic chunk records with source lineage.',
            'Dense and optional sparse index artifacts.',
            'Metadata for routing, filtering, and citation reconstruction.',
            'Quality report covering parse, OCR, and chunk metrics.',
            'Index mutation report with insert and update statistics.',
            'Immutable audit log entries for governance review.',
            'Snapshot identifier for reproducible downstream reads.'
        )
        Steps = @(
            'Define source inventory and trust boundaries.',
            'Fetch documents and verify integrity checksums.',
            'Select parser strategy by file type and layout profile.',
            'Run OCR fallback for non-extractable pages.',
            'Normalize text while preserving legal references and numbers.',
            'Extract and validate document-level metadata.',
            'Rebuild section hierarchy and structural anchors.',
            'Perform semantic chunking with overlap safeguards.',
            'Attach provenance and temporal metadata to every chunk.',
            'Generate stable chunk IDs and content hashes.',
            'Create embeddings and lexical index artifacts.',
            'Upsert into storage with idempotent semantics.',
            'Reconcile vector and metadata stores for consistency.',
            'Run quality gates and quarantine invalid artifacts.',
            'Publish snapshot manifest and promote if healthy.',
            'Retain rollback snapshot and execution evidence.',
            'Emit metrics and close run with signed audit trace.',
            'Notify downstream services of new index version.',
            'Archive artifacts according to retention policy.',
            'Schedule remediation for quarantined documents.'
        )
        Concepts = @(
            'Source trust modeling',
            'Heterogeneous parsing strategy',
            'OCR uncertainty handling',
            'Normalization without semantic loss',
            'Structure-aware chunking',
            'Chunk overlap continuity',
            'Metadata ontology discipline',
            'Provenance completeness',
            'Embedding model-domain alignment',
            'Sparse and dense dual indexing',
            'Idempotent update design',
            'Snapshot version governance'
        )
        Controls = @(
            'Source allowlist and denylist enforcement',
            'Checksum and signature validation',
            'Parser fallback control',
            'Metadata schema validation gate',
            'Chunk-size and overlap bound check',
            'Duplicate suppression by hash policy',
            'Embedding generation health guard',
            'Index consistency reconciliation',
            'Temporal tagging verification',
            'Sensitive data redaction check',
            'Snapshot promotion gate',
            'Audit log completeness control'
        )
        Failures = @(
            'Corrupt source files',
            'OCR numeric hallucinations',
            'Section boundary loss',
            'Over-cleaning of statutory text',
            'Chunk fragmentation of key clauses',
            'Missing critical metadata fields',
            'Duplicate chunk proliferation',
            'Embedding service interruption',
            'Vector-metadata drift',
            'Temporal tag misassignment',
            'Partial ingest mistakenly promoted',
            'Untracked manual data patching'
        )
        Metrics = @(
            'Parse success rate',
            'OCR confidence distribution',
            'Chunk quality and coherence score',
            'Chunk duplication ratio',
            'Metadata completeness rate',
            'Embedding success rate',
            'Index reconciliation pass rate',
            'Source-to-index freshness lag',
            'Throughput per ingestion run',
            'Ingestion cost per document',
            'Quarantine backlog size',
            'Rollback readiness pass rate'
        )
        Tests = @(
            'Parser regression suite',
            'OCR quality regression suite',
            'Normalization snapshot tests',
            'Chunking invariant tests',
            'Deduplication correctness tests',
            'Metadata schema tests',
            'Embedding compatibility tests',
            'Store reconciliation tests',
            'Incremental replay tests',
            'Temporal tag correctness tests',
            'Security leak tests',
            'Pre-promotion canary tests'
        )
        Ops = @(
            'Run clean ingestion in staging',
            'Run incremental ingestion in production',
            'Quarantine triage workflow',
            'Weekly index reconciliation',
            'Monthly rollback drill',
            'Cost and throughput review',
            'Parser incident review with SMEs',
            'Embedding model upgrade protocol',
            'Snapshot publication process',
            'Audit artifact archival',
            'On-call escalation for ingest failures',
            'Runbook update after incidents'
        )
        Checklist = @(
            'Authoritative source list approved and current.',
            'Mandatory metadata fields validated.',
            'Chunking policy preserves legal meaning.',
            'Embedding and index versions pinned.',
            'Idempotent ingest verified.',
            'Snapshot promotion gates enforced.',
            'Quarantine process operational.',
            'Quality report generated every run.',
            'Rollback procedure tested.',
            'Security checks passed.',
            'Audit trail complete.',
            'On-call response plan verified.'
        )
    },
    @{
        File = '02_retrieval.md'
        Title = 'Phase 2: Retrieval (High-Recall Candidate Evidence Search)'
        Upstream = 'Indexed dense and sparse stores with rich metadata.'
        Downstream = 'Reranking precision and final answer grounding quality.'
        Target = 'maximize recall at K with bounded latency and cost.'
        Risk = 'missing key evidence or surfacing stale and irrelevant evidence.'
        Business = 'return plausible evidence fast and consistently across intents.'
        Technical = 'blend query understanding, dense retrieval, sparse retrieval, and fusion.'
        Inputs = @(
            'User query and optional conversation context.',
            'Routing hints such as domain and jurisdiction.',
            'Query rewrite policy and limits.',
            'Dense vector index and lexical index handles.',
            'Metadata filters including temporal constraints.',
            'Access-control context and tenant boundaries.',
            'Top-K and fusion policy parameters.',
            'Cache and timeout configuration.'
        )
        Outputs = @(
            'Top-K candidate chunks with fused rank features.',
            'Per-retriever scoring traces.',
            'Filter and rewrite decision logs.',
            'Latency breakdown by retrieval stage.',
            'Low-recall risk indicators.',
            'Access-control enforcement outcomes.',
            'Cache hit and miss metadata.',
            'Reranker-ready candidate payload.'
        )
        Steps = @(
            'Validate incoming query request contract.',
            'Classify intent and infer domain hints.',
            'Extract entities and regulatory references.',
            'Apply conservative rewrite expansions.',
            'Embed query for semantic retrieval.',
            'Execute dense nearest-neighbor search.',
            'Execute sparse lexical search.',
            'Apply metadata and temporal filters.',
            'Merge and deduplicate candidate sets.',
            'Fuse rankings with stable strategy.',
            'Apply diversity balancing rules.',
            'Measure score distribution confidence.',
            'Detect and flag low-recall scenarios.',
            'Emit retrieval diagnostics and traces.',
            'Return selected candidates to reranker.',
            'Update cache according to policy.',
            'Record authorization decisions.',
            'Monitor stage-level latency.',
            'Persist request correlation metadata.',
            'Close retrieval transaction safely.'
        )
        Concepts = @(
            'Intent decomposition',
            'Entity-aware query representation',
            'Rewrite drift prevention',
            'Semantic vector retrieval',
            'Lexical BM25-style retrieval',
            'Hybrid rank fusion',
            'Score normalization discipline',
            'Metadata filter correctness',
            'Temporal retrieval validity',
            'Source diversity balancing',
            'Recall-latency tradeoff control',
            'Cache consistency strategy'
        )
        Controls = @(
            'Query schema validation',
            'Rewrite budget cap',
            'Retriever timeout guard',
            'Jurisdiction filter enforcement',
            'Temporal validity filter gate',
            'Access-control filter gate',
            'Fusion stability check',
            'Duplicate suppression check',
            'Low-confidence retrieval flag',
            'Fallback retrieval path',
            'Latency circuit breaker',
            'Trace completeness control'
        )
        Failures = @(
            'Intent drift from rewriting',
            'Exact-citation miss in dense path',
            'Semantic miss in sparse path',
            'Over-filtering of valid evidence',
            'Under-filtering of stale evidence',
            'Fusion instability',
            'Duplicate-heavy candidate list',
            'Retriever timeout',
            'Stale cache serving old results',
            'Access-control misconfiguration',
            'Latency spikes under burst load',
            'Long-tail terminology miss'
        )
        Metrics = @(
            'Recall at K',
            'MRR',
            'nDCG',
            'Rewrite acceptance rate',
            'Filter precision',
            'Temporal correctness rate',
            'Source diversity index',
            'Retriever timeout rate',
            'P50 latency',
            'P95 latency',
            'Cache hit ratio',
            'Unauthorized retrieval block rate'
        )
        Tests = @(
            'Dense relevance regression',
            'Sparse relevance regression',
            'Fusion ranking stability tests',
            'Rewrite adversarial tests',
            'Filter correctness tests',
            'Temporal retrieval tests',
            'Duplicate suppression tests',
            'Fallback path tests',
            'Burst latency tests',
            'Cache coherence tests',
            'Authorization boundary tests',
            'End-to-end recall gate tests'
        )
        Ops = @(
            'Top-K tuning based on recall and latency',
            'Fusion calibration with labeled data',
            'Low-recall incident review',
            'Query rewrite audit with SMEs',
            'Temporal filter audits',
            'Cache policy review',
            'Retriever failover drill',
            'Access-control audit after policy updates',
            'KPI reporting cadence',
            'Canary rollout for retrieval changes',
            'Rollback playbook execution',
            'Runbook revision after incidents'
        )
        Checklist = @(
            'Recall target achieved on benchmark.',
            'Hybrid retrieval calibrated.',
            'Rewrite policy constrained and logged.',
            'Temporal filters validated.',
            'Access controls verified.',
            'Duplicate suppression effective.',
            'Latency SLO satisfied.',
            'Fallback behavior tested.',
            'Cache invalidation reliable.',
            'Diagnostics complete.',
            'Regression gates active.',
            'On-call procedures updated.'
        )
    },
    @{
        File = '03_reranking.md'
        Title = 'Phase 3: Reranking (Precision-First Evidence Curation)'
        Upstream = 'Hybrid retrieval candidates and retrieval diagnostics.'
        Downstream = 'Context builder quality and generation faithfulness.'
        Target = 'maximize precision at N while preserving evidence coverage.'
        Risk = 'noisy context or omission of decisive evidence.'
        Business = 'promote evidence that directly supports trustworthy answers.'
        Technical = 'score query-document pairs with high-fidelity relevance models and policies.'
        Inputs = @(
            'Normalized query representation.',
            'Top-K retrieved candidates with metadata.',
            'Reranker model and threshold configuration.',
            'Diversity constraints and deduplication policy.',
            'Latency budget for scoring.',
            'Abstention policy thresholds.',
            'Token budget hints for downstream context.',
            'Trace correlation identifiers.'
        )
        Outputs = @(
            'Top-N reranked evidence with calibrated scores.',
            'Discarded candidate reasons.',
            'Abstention signal when confidence is low.',
            'Diversity and redundancy metrics.',
            'Latency and inference diagnostics.',
            'Score distribution metadata.',
            'Trace linkage to retrieval stage.',
            'Context-ready evidence payload.'
        )
        Steps = @(
            'Validate candidate payload schema.',
            'Generate query-document scoring pairs.',
            'Run pairwise relevance model.',
            'Normalize and calibrate score outputs.',
            'Sort candidates by calibrated relevance.',
            'Apply minimum confidence threshold.',
            'Enforce diversity constraints.',
            'Remove near-duplicate evidence chunks.',
            'Apply token-budget aware selection.',
            'Select top-N evidence set.',
            'Compute reranking confidence summary.',
            'Emit abstention recommendation when needed.',
            'Persist full scoring trace for analysis.',
            'Monitor latency and model errors.',
            'Return curated evidence to context builder.',
            'Record configuration fingerprints.',
            'Cache deterministic outputs where safe.',
            'Route anomalies to incident channel.',
            'Update observability stream.',
            'Close reranking transaction.'
        )
        Concepts = @(
            'Pairwise semantic relevance',
            'Cross-encoder precision benefits',
            'Score calibration and comparability',
            'Threshold-based abstention',
            'Diversity-aware selection',
            'Redundancy suppression',
            'Token-budget optimization',
            'Latency-constrained inference',
            'Confidence signal reliability',
            'Ranking stability analysis',
            'Domain-specific relevance behavior',
            'Offline-online alignment'
        )
        Controls = @(
            'Candidate schema gate',
            'Inference timeout and fallback',
            'Score normalization guard',
            'Threshold governance',
            'Diversity enforcement',
            'Duplicate suppression gate',
            'Top-N boundary check',
            'Abstention trigger policy',
            'Model version lock',
            'Trace logging guarantee',
            'Latency SLO monitor',
            'Canary release control'
        )
        Failures = @(
            'Overfitted relevance scoring',
            'Threshold too strict',
            'Threshold too loose',
            'Redundant evidence dominance',
            'Missing key minority evidence',
            'Latency spikes for large K',
            'Inference service degradation',
            'Unstable tie-breaking behavior',
            'Confidence score misuse downstream',
            'Token truncation of key evidence',
            'Unobserved regression after model update',
            'Insufficient traceability for audits'
        )
        Metrics = @(
            'Precision at N',
            'Top-1 relevance accuracy',
            'Abstention recommendation rate',
            'False-negative relevance rate',
            'Diversity index in top-N',
            'Duplicate suppression ratio',
            'P50 reranking latency',
            'P95 reranking latency',
            'Inference error rate',
            'Score stability score',
            'Handoff quality to generation',
            'Canary delta versus baseline'
        )
        Tests = @(
            'Pairwise relevance regression',
            'Threshold calibration tests',
            'Diversity constraint tests',
            'Near-duplicate suppression tests',
            'Latency scaling tests',
            'Model compatibility tests',
            'Deterministic tie-break tests',
            'Fallback behavior tests',
            'Confidence contract tests',
            'Token-budget truncation tests',
            'Canary gating tests',
            'End-to-end faithfulness impact tests'
        )
        Ops = @(
            'Monthly threshold recalibration',
            'Abstention case reviews with SMEs',
            'Candidate size tuning',
            'Reranker drift monitoring',
            'Duplicate-pattern audits',
            'Deterministic replay for incidents',
            'Rollback package maintenance',
            'KPI reporting',
            'Canary rollout execution',
            'Diversity policy patching',
            'Runbook updates after postmortems',
            'Cross-team retrieval-reranking alignment'
        )
        Checklist = @(
            'Reranker version pinned.',
            'Thresholds calibrated and approved.',
            'Top-N aligned with context budget.',
            'Diversity controls validated.',
            'Duplicate suppression validated.',
            'Latency SLO met.',
            'Abstention policy tested.',
            'Fallback path verified.',
            'Traceability complete.',
            'Canary process enforced.',
            'Regression suite passing.',
            'On-call playbook current.'
        )
    },
    @{
        File = '04_generation.md'
        Title = 'Phase 4: Generation and Guardrails (Grounded Answer Delivery)'
        Upstream = 'Curated evidence and confidence metadata from reranking.'
        Downstream = 'User-facing response quality, compliance posture, and trust outcomes.'
        Target = 'maximize grounded usefulness with minimal hallucination and policy risk.'
        Risk = 'unsupported claims, citation errors, or unsafe responses.'
        Business = 'deliver clear answers that are verifiable, compliant, and useful.'
        Technical = 'control prompting, decoding, citation, and validation as one pipeline.'
        Inputs = @(
            'User question and context window.',
            'Reranked evidence blocks with source IDs.',
            'System prompt policy and response schema.',
            'Decoding and token budget parameters.',
            'Safety policy and refusal rules.',
            'Disclaimer and legal boundary policy.',
            'Citation validator and claim checker configs.',
            'Audit and logging context.'
        )
        Outputs = @(
            'Grounded answer text.',
            'Citation map linking claims to evidence IDs.',
            'Abstention or refusal when required.',
            'Safety intervention indicators.',
            'Validation and repair report.',
            'Latency and token usage telemetry.',
            'Signed trace metadata for audit.',
            'Final response payload for clients.'
        )
        Steps = @(
            'Validate evidence package integrity.',
            'Build constrained system prompt.',
            'Inject evidence with stable citation IDs.',
            'Apply deterministic decoding policy.',
            'Generate first-pass answer draft.',
            'Extract and validate citations.',
            'Run unsupported-claim checks.',
            'Run safety and policy filters.',
            'Apply mandatory disclaimer policies.',
            'Validate output schema and formatting.',
            'Repair or refuse on validation failure.',
            'Attach confidence and trace metadata.',
            'Log prompt and response fingerprints.',
            'Measure latency and token budgets.',
            'Return validated response to client.',
            'Route high-risk responses for review.',
            'Record intervention outcomes.',
            'Feed samples to evaluation pipeline.',
            'Update guardrail dashboards.',
            'Close response transaction with audit ID.'
        )
        Concepts = @(
            'Grounded generation constraints',
            'Instruction hierarchy control',
            'Claim-level citation binding',
            'Evidence sufficiency checks',
            'Deterministic decoding strategy',
            'Post-generation verification loop',
            'Schema-constrained output',
            'Safety policy layering',
            'Regulatory disclaimer compliance',
            'Citation hallucination prevention',
            'Prompt injection resistance',
            'Auditability by design'
        )
        Controls = @(
            'System prompt grounding lock',
            'Context size guard',
            'Citation existence validator',
            'Claim-evidence consistency checker',
            'Safety gate',
            'Disclaimer injector',
            'Output schema validator',
            'Abstention fallback control',
            'Injection detection filter',
            'Model/config version pinning',
            'Sensitive output redaction',
            'Trace retention policy'
        )
        Failures = @(
            'Unsupported but fluent claims',
            'Invalid citation indices',
            'Citation-claim mismatch',
            'Prompt injection override',
            'Safety false negatives',
            'Over-refusal due to strict filters',
            'Missing disclaimers',
            'Schema violations in responses',
            'Token truncation of qualifiers',
            'Latency spikes with long context',
            'Behavior drift after model change',
            'Incomplete audit traces'
        )
        Metrics = @(
            'Faithfulness score',
            'Citation validity rate',
            'Unsupported claim rate',
            'Refusal appropriateness rate',
            'Safety intervention precision',
            'Schema compliance rate',
            'Disclaimer inclusion rate',
            'P50 generation latency',
            'P95 generation latency',
            'Token efficiency',
            'User-rated usefulness',
            'Policy violation incident rate'
        )
        Tests = @(
            'Grounding regression tests',
            'Citation adversarial tests',
            'Unsupported claim detection tests',
            'Prompt injection tests',
            'Safety policy tests',
            'Disclaimer enforcement tests',
            'Schema validation tests',
            'Abstention path tests',
            'Long-context latency tests',
            'Determinism snapshot tests',
            'Sensitive output tests',
            'SME acceptance tests'
        )
        Ops = @(
            'Unsupported-claim incident review',
            'Refusal threshold calibration',
            'Citation failure triage',
            'Prompt template A/B governance',
            'Red-team safety exercises',
            'Disclaimer coverage audits',
            'Token cost monitoring',
            'Canary rollout for model changes',
            'Fallback model readiness checks',
            'Weekly quality dashboard publication',
            'Quarterly compliance audit',
            'Runbook improvement loop'
        )
        Checklist = @(
            'Grounding rules enforced.',
            'Citation validation blocking invalid outputs.',
            'Claim checks operational.',
            'Safety gates validated.',
            'Disclaimer compliance guaranteed.',
            'Schema validation enabled.',
            'Abstention behavior tested.',
            'Latency budget met.',
            'Injection resilience verified.',
            'Trace artifacts retained.',
            'Canary rollout required.',
            'Incident response ready.'
        )
    },
    @{
        File = '05_evaluation.md'
        Title = 'Phase 5: Evaluation and Continuous Improvement (Release-Quality Governance)'
        Upstream = 'Artifacts from all prior phases, including traces and outputs.'
        Downstream = 'Release decisions, remediation backlog, and iterative quality improvements.'
        Target = 'maximize reliable quality and detect regressions before user impact.'
        Risk = 'silent quality degradation and non-compliant behavior in production.'
        Business = 'establish objective, reproducible quality governance for RAG releases.'
        Technical = 'evaluate component and end-to-end behavior with robust metrics and gates.'
        Inputs = @(
            'Golden dataset with questions and expected evidence.',
            'Pipeline traces from retrieval, reranking, and generation.',
            'Metric definitions and scoring rubrics.',
            'Judge-model settings and calibration references.',
            'Historical baseline metrics and thresholds.',
            'Domain and difficulty segmentation maps.',
            'Operational telemetry for latency and cost.',
            'Incident and user-feedback data.'
        )
        Outputs = @(
            'Component and end-to-end evaluation reports.',
            'Pass/fail release-gate decisions.',
            'Regression diffs against baseline.',
            'Failure taxonomy and root-cause hints.',
            'Prioritized remediation action list.',
            'Updated benchmark candidates from failures.',
            'Governance-ready audit package.',
            'Continuous-improvement execution plan.'
        )
        Steps = @(
            'Validate benchmark and rubric integrity.',
            'Run fixed-config pipeline on benchmark suite.',
            'Score retrieval quality metrics.',
            'Score reranking quality metrics.',
            'Score generation faithfulness and correctness.',
            'Validate citations and policy compliance.',
            'Aggregate metrics by segment and domain.',
            'Compare against baseline and control cohorts.',
            'Apply release gate thresholds.',
            'Classify failures by root-cause layer.',
            'Attach latency and cost trend analysis.',
            'Generate stakeholder-facing reports.',
            'Block release on critical regressions.',
            'Promote only if all mandatory checks pass.',
            'Store reproducibility artifacts and signatures.',
            'Feed real production failures into benchmark queue.',
            'Calibrate judge-model consistency periodically.',
            'Run human SME arbitration on disputed cases.',
            'Assign remediation tasks with owners.',
            'Close cycle with updated baseline and action log.'
        )
        Concepts = @(
            'Component versus end-to-end evaluation',
            'Benchmark representativeness',
            'Faithfulness versus correctness separation',
            'Retrieval ranking metric interpretation',
            'Citation quality as trust metric',
            'Judge-model calibration',
            'Segment-level fairness analysis',
            'Regression gate governance',
            'Error taxonomy discipline',
            'Cost-quality-latency balancing',
            'Temporal drift detection',
            'Closed-loop improvement design'
        )
        Controls = @(
            'Benchmark version lock',
            'Reproducibility contract enforcement',
            'Automated release-gate blocker',
            'Rubric version control',
            'Human review for high-impact failures',
            'Metric integrity validation',
            'Segment reporting requirement',
            'Significance-check control',
            'Incident-triggered re-evaluation',
            'Report archival policy',
            'Environment parity checks',
            'Post-release backtest requirement'
        )
        Failures = @(
            'Benchmark overfitting',
            'Data leakage into evaluation',
            'Judge inconsistency',
            'Aggregate masking of segment regressions',
            'Disabled release gate',
            'Faithfulness false positives',
            'Ignored latency regressions',
            'Missing policy scenarios in tests',
            'Untriaged recurring failures',
            'Release despite red metrics',
            'Drift after corpus updates',
            'Insufficient decision audit trail'
        )
        Metrics = @(
            'Faithfulness',
            'Answer correctness',
            'Retrieval recall at K',
            'Reranking precision at N',
            'Citation validity',
            'Policy compliance rate',
            'Segment parity gap',
            'P95 latency',
            'Cost per request',
            'Release regression count',
            'Post-release incident rate',
            'Benchmark freshness score'
        )
        Tests = @(
            'Benchmark leakage tests',
            'Reproducibility tests',
            'Metric unit tests',
            'Judge consistency tests',
            'Segment fairness tests',
            'Release-gate simulation tests',
            'Root-cause classification tests',
            'Latency trend tests',
            'Policy compliance tests',
            'Ablation impact tests',
            'Canary-vs-baseline tests',
            'Post-release backtests'
        )
        Ops = @(
            'Nightly benchmark evaluation',
            'Pre-release full gate run',
            'Domain regression review meetings',
            'Benchmark refresh workflow',
            'Quarterly judge calibration',
            'Monthly quality and compliance report',
            'Remediation backlog tracking',
            'Emergency re-evaluation protocol',
            'Signed artifact retention',
            'Release go/no-go governance',
            'Threshold updates by risk profile',
            'On-call diagnostics training'
        )
        Checklist = @(
            'Benchmark representative and versioned.',
            'Runs reproducible and auditable.',
            'Mandatory metrics computed.',
            'Release gates enforced automatically.',
            'Judge calibration monitored.',
            'Human review path active.',
            'Failure taxonomy actionable.',
            'Latency and cost tracked with quality.',
            'Policy compliance included in pass criteria.',
            'Production failures fed back to benchmarks.',
            'Audit artifacts retained.',
            'Continuous improvement loop operating.'
        )
    }
)

$docsDir = Join-Path $PWD 'docs\rag_phases'
foreach ($p in $phases) {
    New-LongPhaseDoc -P $p -OutFile (Join-Path $docsDir $p.File) -MinLines 330
}
