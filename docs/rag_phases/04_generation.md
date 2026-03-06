# Phase 4: Generation & Guardrails

The Generation phase is where the "R" (Retrieval) and "A" (Augmented) meet the "G" (Generation). This is the final step where the system synthesizes a human-readable answer while strictly adhering to the provided facts.

## 🏗️ The Generation Ecosystem

### 1. High-Speed LLM Integration (`llm_client.py`)
The system integrates with **Groq**, an AI infrastructure provider known for extremely low-latency inference.
- **Model Choice**: Primarily `llama-3.1-8b-instant`. This model is large enough to follow complex legal instructions but fast enough to provide answers in under 1 second.
- **Parameters**:
    - `temperature=0.0`: We set temperature to zero to make the model "greedy" and deterministic. This prevents it from getting creative or "hallucinating" facts that aren't in the context.
    - `max_tokens=1024`: Large enough for detailed answers but keeps responses concise.

### 2. Prompt Engineering (`prompts/`)
The effectiveness of our RAG system relies on a complex **System Prompt** that acts as the "Laws of the Robot":
- **Persona**: The LLM is instructed to act as a "Tax and Finance Expert for Indian Regulations."
- **Strict Grounding**: The prompt contains a rule: *"If the answer is not in the context, state that you do not know. Do not use outside knowledge."*
- **Citation Syntax**: The LLM is forced to use numerical citations (e.g., `[1]`, `[2]`) immediately after every claim it makes.

### 3. Safety Guardrails (`guardrails.py`)
To make the system "Production-Ready," we implement multiple layers of protection:
- **Topic Filtering**: An input guardrail checks if the user is asking about irrelevant or harmful topics.
- **Hallucination Detection**: If the reranking score from Phase 3 was too low, the generation phase might be skipped entirely in favor of a safe "I could not find relevant documentation" message.
- **Disclaimer Injection**: Legally, as an AI, we must not give financial advice. The system automatically appends a mandatory disclaimer to every response, even if the LLM forgets to include it.

### 4. Citation Mapping & Validation (`citation_mapper.py`)
Citations are the key to trust.
- **Regex Verification**: A post-processor runs after the LLM finishes generating. It uses Regular Expressions to find all `[n]` occurrences.
- **Source Integrity**: It verifies that if the model cites `[3]`, there was actually a 3rd source provided in the context. If the model hallucinations a citation number, the validator flags it.

## 🔄 The Generation Workflow

1.  **Context Assembly**: Merge the top 5 chunks into a formatted string with `<source_id>` tags.
2.  **Prompt Construction**: Inject the query and assembled context into the Llama-3 prompt template.
3.  **Inference**: Send the request to Groq and receive the streamed or batch response.
4.  **Structural Validation**:
    - Does it have citations?
    - Does it have the required disclaimer?
    - Is it formatted correctly (Markdown)?
5.  **Final Delivery**: Return the validated answer, along with the source metadata, to the user interface.

## ⚙️ Key Configurations
- `GROQ_MODEL`: Switch between 8B (speed) and 70B (complex reasoning) models.
- `ENABLE_GUARDRAILS`: Control the strictness of the safety layer.
- `TEMPERATURE`: Always kept at 0.0 for factual accuracy.
