# Phase 5: Automated Evaluation

To measure the quality of the RAG system, an automated evaluation framework is used. This ensures that changes to the code or prompt don't degrade the system's performance.

## 🏗️ Components

### 1. Golden Dataset (`golden_dataset.py`)
- **Content**: A collection of 30+ expert-verified Question/Answer pairs across Tax, Finance, and Legal domains.
- **Role**: Serves as the "Ground Truth" for testing.

### 2. Metrics Engine (`evaluator.py`)
- **Faithfulness**: measures if the generated answer is derived *only* from the retrieved context.
- **Correctness**: Compares the generated answer to the reference answer in the Golden Dataset.
- **Citation Quality**: Checks if citations are present and valid.
- **Retrieval Relevance**: Evaluates if the retrieved chunks were actually useful for answering the question.

### 3. CI/CD Integration (`evaluation_gate.py`)
- **Quality Gate**: A script used in GitHub Actions that fails the build if passing metrics drop below a set threshold (e.g., pass rate < 0.8).

## 🔄 Evaluation Workflow

1. **Query Run**: Run the entire RAG pipeline for every question in the Golden Dataset.
2. **Score Calculation**: Use a "judge" LLM (usually a larger model like Llama-3-70B) to score the responses using the metrics defined above.
3. **Report Generation**: Output results to `evaluation/reports/`.

## 📈 Metric Thresholds

| Metric | Threshold |
|---|---|
| Faithfulness | ≥ 0.70 |
| Correctness | ≥ 0.60 |
| Citation Quality | ≥ 0.80 |
| Retrieval Relevance | ≥ 0.50 |

## 🛠️ Usage

To run the full evaluation suite:
```bash
make evaluate
```
This generates a detailed report summarizing the system's accuracy and reliability.
