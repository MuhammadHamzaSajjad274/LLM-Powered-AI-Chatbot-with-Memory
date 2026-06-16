# LLM-Powered AI Chatbot with Long-Term Memory

A production-ready RAG chatbot with persistent memory, streaming responses, multi-backend LLM support, and MLflow observability. Built with Streamlit, ChromaDB, and sentence-transformers.

## Features

- **RAG pipeline** with cosine similarity filtering over stored conversation chunks
- **Long-term memory** via ChromaDB with automatic summarization every 20 turns
- **Streaming token output** for low perceived latency
- **Multi-backend LLM** — local Mistral 7B, HuggingFace Inference API, OpenAI, Deepseek
- **MLflow observability dashboard** — latency, relevance, and response metrics
- **Modern Streamlit UI** with animated landing screen and glassmorphism chat design
- **Docker-ready** deployment with model volume mounting
- **pytest test suite** with mocked dependencies

## Project Structure

```
llm-chatbot-memory/
├── app.py                      # Streamlit UI (landing + chat)
├── main.py                     # RAG pipeline orchestrator
├── requirements.txt
├── configs/model_config.yaml   # LLM + memory configuration
├── core/
│   ├── llm.py                  # LLM abstraction (local, HF, OpenAI, Deepseek)
│   ├── embeddings.py           # sentence-transformers embedder
│   ├── retriever.py            # ChromaDB vector search
│   ├── memory.py               # Conversation memory + summarization
│   ├── observability.py        # MLflow logging
│   └── utils.py                # Config + helpers
├── pages/dashboard.py          # MLflow observability dashboard
├── tests/                      # pytest unit tests
├── deployment/Dockerfile
├── models/                     # Local .gguf models (gitignored)
└── vectorstore/chroma_db/      # Persistent ChromaDB (gitignored)
```

## Quick Start

### Prerequisites

- Python 3.10+
- pip
- (Optional) HuggingFace, OpenAI, or Deepseek API key

### Installation

```bash
git clone https://github.com/(replace with your GitHub username)/llm-chatbot-memory.git
cd llm-chatbot-memory
```

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

---

### Option A — Local (Mistral 7B GGUF)

**Step 1 — Download model**

Place `mistral-7b-instruct-v0.2.Q4_K_M.gguf` in the `models/` folder.

**Step 2 — Configure**

In `configs/model_config.yaml`:

```yaml
llm:
  type: "local"
```

**Step 3 — Run**

```bash
streamlit run app.py
```

Open **http://localhost:8501**

---

### Option B — HuggingFace Inference API (recommended for demo)

**Step 1 — Get token**

Create a token at [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

**Step 2 — Configure `.env`**

```env
HF_API_TOKEN=your-actual-token-here
```

**Step 3 — Configure**

In `configs/model_config.yaml` set:

```yaml
llm:
  type: "huggingface"
```

**Step 4 — Run**

```bash
streamlit run app.py
```

Open **http://localhost:8501**

---

### Option C — OpenAI (GPT-3.5-turbo)

Add `OPENAI_API_KEY` to `.env` and set `llm.type: "openai"` in `configs/model_config.yaml`.

```bash
streamlit run app.py
```

---

## MLflow Dashboard

```bash
streamlit run app.py
# Click "dashboard" in the sidebar
```

Shows: total queries, avg latency, chunk retrieval rate, response length trends over time.

Optional MLflow UI:

```bash
mlflow ui --backend-store-uri ./mlflow_runs
```

---

## Docker

```bash
docker build -t llm-chatbot .
docker run -v /path/to/models:/app/models -p 8501:8501 llm-chatbot
```

---

## Tests

```bash
pytest tests/ -v
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit + custom CSS |
| LLM (local) | Mistral 7B Q4 via llama-cpp-python |
| LLM (cloud) | HuggingFace Inference API / OpenAI |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Store | ChromaDB (persistent, cosine similarity) |
| Observability | MLflow |
| Testing | pytest |
| Deployment | Docker |

---

## CV Highlights

- Built end-to-end RAG pipeline with cosine similarity filtering 
  (distance threshold < 0.4) over conversation history
- Implemented streaming token output reducing perceived latency
- Added MLflow observability tracking latency, relevance scores, 
  and response metrics per query
- Designed modular LLM abstraction supporting 3 backends 
  with zero code changes via config
- Unit tested memory, retriever, and LLM components with pytest 
  using mocked dependencies

---

## License

MIT License — see [LICENSE](LICENSE) for details.
