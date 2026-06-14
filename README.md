# LegalFinance AI 🏛️📈

![Version](https://img.shields.io/badge/version-1.0.4--Stable-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)

LegalFinance AI is a state-of-the-art **Retrieval-Augmented Generation (RAG) system** engineered specifically for the Indian legal and financial domain. It securely indexes, retrieves, and synthesizes complex government documents, tax regulations, and budget speeches to provide accurate, citable, and professional answers.

Live Demo: [legal-finance-rag.vercel.app](https://legal-finance-rag.vercel.app)

## ✨ Core Features

*   **Hybrid Search with RRF:** Merges dense vector embeddings (Semantic Search) and sparse BM25 (Keyword Search) using Reciprocal Rank Fusion for unparalleled retrieval accuracy.
*   **Cross-Encoder Re-ranking:** Re-evaluates and strictly orders the retrieved chunks using a cross-encoder model to ensure maximum relevance before feeding into the LLM context window.
*   **Personal Knowledge Base:** Users can seamlessly upload their own PDFs (like resumes, contracts, or tax documents) directly from the UI. The system intelligently fuses user-uploaded documents with the system-wide legal corpus.
*   **Agentic Tool Orchestrator:** The LLM acts as an autonomous agent, equipped with tools to query real-time budget data, lookup specific Act sections, or trigger deep document searches.
*   **Zero-Retention Privacy Mode:** Designed for sensitive financial data—user conversations and temporary uploads are not persistently stored on the server.
*   **Export & Compliance:** Built-in PDF export capabilities for entire chat threads, alongside strictly enforced legal and financial disclaimers for every AI generation.
*   **Premium "Black & Gold" UI:** A beautifully crafted, responsive Next.js frontend utilizing Tailwind CSS, Lucide Icons, and smooth micro-animations.

## 🏗️ Architecture

The repository is structured as a full-stack monorepo:

### Backend (`/app`)
*   **Framework:** FastAPI
*   **Orchestration:** LangChain / Custom Tool Executor
*   **Vector Database:** ChromaDB
*   **Embeddings:** HuggingFace `all-MiniLM-L6-v2`
*   **Cross-Encoder:** `cross-encoder/ms-marco-MiniLM-L-6-v2`
*   **Caching:** Redis-backed TTL query cache

### Frontend (`/frontend-nextjs`)
*   **Framework:** Next.js 14 (App Router)
*   **Styling:** Tailwind CSS with a curated Dark/Gold aesthetic
*   **Components:** Radix UI / Custom functional components
*   **State Management:** React Hooks

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Redis (Optional, for caching)

### Backend Setup
```bash
# 1. Clone the repository
git clone https://github.com/Nikil-R/Legal_Finance_RAG.git
cd Legal_Finance_RAG

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your LLM API keys (e.g., Groq, OpenAI)

# 5. Run the FastAPI server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
# 1. Navigate to the frontend directory
cd frontend-nextjs

# 2. Install dependencies
npm install

# 3. Run the development server
npm run dev
```
Navigate to `http://localhost:3000` to view the application.

## 🧠 How the RAG Pipeline Works
1.  **Query Processing:** The user's query is ingested and evaluated by a Guardrail Engine to ensure it meets safety and domain criteria.
2.  **Hybrid Retrieval:** The system simultaneously queries BM25 and Vector DB across both the **System Corpus** (Government Acts, Budgets) and the **User Corpus** (Uploaded PDFs).
3.  **Fusion (RRF):** Results are merged and normalized using Reciprocal Rank Fusion.
4.  **Re-ranking:** A Cross-Encoder heavily penalizes irrelevant chunks, ensuring only the top `N` most contextually accurate paragraphs survive.
5.  **Generation:** The Tool Orchestrator supplies the LLM with the highly-curated context chunks to generate a synthesized answer, appending robust citations and latency metrics.

## 📜 License
This project is licensed under the MIT License.

---
*Disclaimer: LegalFinance AI provides information for educational and reference purposes only. It is NOT a substitute for professional legal, tax, or financial advice. All results are AI-generated and should be verified with official portals or qualified professionals.*