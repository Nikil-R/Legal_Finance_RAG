# Phase 5: Automated Evaluation

"If you can't measure it, you can't improve it." 

RAG systems are notoriously difficult to test because natural language is subjective. To solve this, LegalFinance RAG uses an **Automated Evaluation Pipeline** that measures mathematical accuracy and semantic grounding.

## 🏗️ Components of Evaluation

### 1. The Golden Dataset (`golden_dataset.py`)
This is our "Ground Truth." It consists of a curated YAML/JSON file containing:
- **Expert Questions**: Real-world queries about GST, Income Tax, and Companies Act.
- **Reference Answers**: Ideal, verified answers that the system *should* produce.
- **Support Documents**: The exact files that contain the answer.
- **Difficulty Levels**: Categorized (Easy, Medium, Hard) to track performance across complexity.

### 2. The Four Pillars of Metrics (`evaluator.py`)

We use what is known as the "RAG Triad" plus additional checks:

#### A. Faithfulness (Grounding)
- **Question**: Is the answer derived *only* from the retrieved context?
- **How**: A "Judge LLM" extracts every claim in the answer and verifies if it is supported by the context.
- **Pass Threshold**: ≥ 0.70

#### B. Answer Correctness
- **Question**: Does the answer match the reference answer in the Golden Dataset?
- **How**: Measures semantic similarity between the generated and expected answers, and checks for "required keywords" (e.g., specific percentage rates or section numbers).
- **Pass Threshold**: ≥ 0.60

#### C. Retrieval Relevance
- **Question**: Were the 20 chunks retrieved in Phase 2 actually relevant to the question?
- **How**: Checks if the "Correct" document (as defined in the Golden Dataset) was present in the top-K retrieved results.
- **Pass Threshold**: ≥ 0.50

#### D. Citation Quality
- **Question**: Are the citations accurate and present?
- **How**: Verifies that `[1]` actually points to the correct document and that the mandatory disclaimer is included.
- **Pass Threshold**: ≥ 0.80

### 3. The "Judge LLM" Concept
To calculate these scores, we use a larger LLM (e.g., Llama-3-70B or GPT-4o) as an independent judge. It follows strict rubrics to assign numerical scores to each response, providing objectivity that simple code cannot.

## 🔄 The Evaluation Workflow

1.  **Run Pipeline**: For every question in the Golden Dataset, trigger the full RAG system (Retrieval -> Reranking -> Generation).
2.  **Collect Data**: Save the generated answer, the retrieved chunks, and the time taken.
3.  **Audit**: Pass these outputs to the Evaluator (Judge LLM).
4.  **Aggregate**: Calculate averages across all questions and domains (Tax vs Finance vs Legal).
5.  **Quality Gate**: If the overall **Pass Rate** is below 80%, the CI/CD pipeline (GitHub Actions) will block the code merge.

## 📊 Reporting (`reporter.py`)
After evaluation, a report is generated (e.g., `evaluation/reports/latest.txt`) which includes:
- **Per-domain success rate**: Are we better at Tax than Legal?
- **Failure Analysis**: Which specific questions failed and why? (e.g., "Hallucination on GST rate").
- **Latency Tracking**: How long did each stage take (p95 latency).

## 🛠️ Usage

To run the evaluation:
```bash
make evaluate
```
This ensures that any change you make to the code (e.g., changing the chunk size or the LLM model) is scientifically proven to be an improvement.
