# Phase 4: Generation & Guardrails

The Generation phase uses a Large Language Model (LLM) to synthesize a final answer based on the retrieved and reranked context.

## 🏗️ Components

### 1. LLM Integration (`llm_client.py`)
- **Provider**: Groq API.
- **Model**: Llama-3 (e.g., `llama-3.1-8b-instant`).
- **Control**: Sets `temperature=0.0` to ensure deterministic, factual responses.

### 2. Citation Mapping (`citation_mapper.py`)
- **Purpose**: Enforces grounding.
- **Mechanism**: Instructs the LLM to use numerical citations (e.g., `[1]`, `[2]`) in its response.
- **Mapping**: Post-processes the response to ensure citations correctly link back to the source IDs in the provided context.

### 3. Safety Guardrails (`guardrails.py`)
- **Input Guard**: Prevents prompt injection or queries about non-legal/non-financial topics.
- **Retrieval Guard**: If reranking scores are too low, the system returns a standard "I don't know" rather than hallucinating.
- **Output Guard**: Ensures no sensitive PII is leaked and that the mandatory legal disclaimer is attached.

### 4. Response Validation (`response_validator.py`)
- **Logic**: Verifies the structural integrity of the output (JSON format, Presence of answer/sources).

## 🔄 Generation Workflow

1. **Prompt Construction**: Combines the User Query, Reranked Context, and Persona (Legal/Financial Expert) into a single prompt.
2. **LLM Call**: Sends the prompt to Groq.
3. **Citation Check**: Verifies that every claim has a corresponding source.
4. **Disclaimer Attachment**: appends the mandatory disclaimer stating that the tool is for educational purposes only.

## ⚙️ Configuration
- `GROQ_MODEL`: The specific Llama variant used.
- `ENABLE_GUARDRAILS`: Toggle safety checks (default: true).
