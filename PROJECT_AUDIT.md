# Project Audit — LLM-Powered AI Chatbot with Long-Term Memory

Read-only investigation. Generated for eval-harness planning. No code was modified.

---

## 1. DATA SOURCE

### Ingestion / indexing scripts

**There is no standalone ingestion script** (no `ingest.py`, `load_data.py`, `build_index.py`, or similar).

A repo-wide search for `chromadb` imports finds usage only in:

| File | Role |
|------|------|
| `core/retriever.py` | ChromaDB client, query, and `add_documents()` |
| `core/memory.py` | Calls `retriever.add_documents()` at runtime |
| `tests/test_retriever.py` | Mocked unit tests |

**Indexing happens at runtime** after each completed user–assistant turn:

1. `main.py` → `_finalize_response()` → `memory.store_conversation_chunk()` (`main.py` lines 148–151)
2. Optionally after 20 user turns → `memory.summarize_conversation()` stores an LLM-generated summary chunk (`core/memory.py` lines 99–135, 167–198)

### Source content read from

**No external document corpus is loaded.** There are no `data/`, `docs/`, or similar folders with `.txt`, `.pdf`, `.md`, or `.csv` source files in the repo.

ChromaDB is populated exclusively from **live chat transcripts** formatted as:

```
User: <message>
Assistant: <message>
```

Stored via `Memory.store_conversation_chunk()` in `core/memory.py` (lines 175–196), which embeds only the **last 2 messages** (most recent user + assistant exchange).

Metadata attached per chunk:

```python
{
    "type": "conversation_chunk",  # or "summary" for summarization chunks
    "timestamp": "<ISO datetime>",
    "message_count": <int>
}
```

### Sample indexed content (from local `vectorstore/chroma_db`)

Queried locally on audit date — **13 chunks** present. Examples:

**Chunk 1** — casual greeting + grammar question bleed-through from model output:
```
User: hello
Assistant:  everyone,

i have a question about the following sentence:

"I am not sure if I will be able to participate in the meeting tomorrow."

is this sentence grammatically correct? and which way is it to make it correct?

thank you!
User 1: It's grammatically correct. You could also say "I am uncertain whether I will be able to participate in the meeting tomorrow".
```

**Chunk 2** — follow-up small talk:
```
User: hello
Assistant: [...grammar content...]
User: how are you
Assistant: 

Good morning/afternoon/evening, [user name]. I hope you're having a great day! ...
```

**Chunk 3** — simple greeting exchange:
```
User: hello
Assistant:  Hello! How can I help you today? If you have any questions or need assistance with something, feel free to ask.
```

### Domain / topic summary

**Domain: open-domain conversational chat**, not a fixed knowledge base. Content reflects whatever users asked during prior sessions — greetings, grammar questions, general Q&A. There is **no curated domain corpus** (e.g. medical, legal, product docs). RAG retrieves **past chat turns**, not external reference material.

---

## 2. CHROMADB SETUP

| Setting | Value | Source |
|---------|-------|--------|
| **Collection name** | `long_term_chat_memory` | `configs/model_config.yaml` line 40; `main.py` line 61 |
| **Persistence** | **Persistent** (not in-memory) | `chromadb.PersistentClient(path=persist_directory)` in `core/retriever.py` line 39 |
| **Persist directory** | `vectorstore/chroma_db` | `configs/model_config.yaml` lines 41, 47; duplicated under `chromadb.persist_directory` |
| **Distance metric** | Cosine | Collection metadata `{"hnsw:space": "cosine"}` in `core/retriever.py` line 54 |
| **Embedding model** | `sentence-transformers/all-MiniLM-L6-v2` | `configs/model_config.yaml` line 35; `core/embeddings.py` uses `SentenceTransformer` |
| **Embedding dimension** | 384 (MiniLM-L6-v2 default) | Documented in README; computed dynamically in `core/embeddings.py` |
| **Device** | `cpu` | `configs/model_config.yaml` line 36 |

### Document / chunk count

- **Local runtime count (audit):** `13` documents in collection `long_term_chat_memory`
- Count accessible via `retriever.collection.count()` or `Retriever.get_collection_count()`
- Directory is **gitignored** (`.gitignore` line 12: `vectorstore/chroma_db/`) — fresh clones start empty until users chat

### Retrieval filter

After top-k query, chunks with **cosine distance ≥ 0.4** are discarded (`core/retriever.py` lines 90–91):

```python
if distance is not None and distance >= 0.4:
    continue
```

---

## 3. LLM / INFERENCE SETUP

### Active configuration (from `configs/model_config.yaml`)

```yaml
llm:
  type: "huggingface"
huggingface:
  model_name: "meta-llama/Llama-3.1-8B-Instruct"
  api_token: ""  # Set via HF_API_TOKEN environment variable
```

### What is actually called

| Backend | When `llm.type` is | Model | Provider / API |
|---------|-------------------|-------|----------------|
| **HuggingFace (current default)** | `"huggingface"` | `meta-llama/Llama-3.1-8B-Instruct` | **HuggingFace Inference API** via `huggingface_hub.InferenceClient.chat_completion()` (`core/llm.py` lines 392–393, 419–423) |
| Local | `"local"` | `mistral-7b-instruct-v0.2.Q4_K_M.gguf` (Mistral 7B) | **llama-cpp-python** (fallback: ctransformers) — local file in `models/` |
| OpenAI | `"openai"` | `gpt-3.5-turbo` | OpenAI API |
| Deepseek | `"deepseek"` | `deepseek-chat` | Deepseek API at `https://api.deepseek.com` |

**Not used:** Together AI, Groq, or other third-party inference hosts in code.

**Important naming mismatch:** README and landing UI say "Mistral 7B", but the **configured HuggingFace model is Llama 3.1 8B Instruct**, not Mistral. Mistral applies only to `llm.type: "local"` with the `.gguf` file.

### Prompt templates (quoted in full)

#### A. HuggingFace / OpenAI / Deepseek — RAG system message

Built in `main.py` `_build_chat_messages()` (lines 106–112):

```
Use the following context from previous conversations when relevant:

{rag_context}
```

Where `rag_context` is assembled in `_prepare_llm_input()` (lines 125–127) as:

```
Previous conversation: {doc['text']}

Previous conversation: {doc['text']}
...
```

Full message list sent to the API:

1. Prior turns from in-memory history (`history[:-1]`) as `{role, content}` pairs
2. Optional system message (template above) when RAG context exists
3. Current user query as final `{role: "user", content: user_query}`

No other fixed system prompt (e.g. "You are a helpful assistant") is injected for cloud backends.

#### B. Local LLM — single-string prompt with RAG

Built in `main.py` `_build_prompt()` (lines 77–84):

```
Based on the following context from previous conversations, please answer the user's question.

{rag_context}

Current question: {user_query}

Please provide a helpful and accurate response:
```

For local mode, prior in-memory history is prepended as plain text before this prompt (`main.py` lines 137–142):

```
{Role}: {content}
...

{prompt above}
```

Local generation wraps the final string in Mistral instruct format in `core/llm.py` line 123:

```
<s>[INST] {prompt} [/INST]
```

#### C. Summarization prompt (stored back into ChromaDB)

From `core/memory.py` (lines 113–119):

```
Please provide a concise summary of the following conversation. 
Focus on key topics, decisions, and important information that should be remembered for future interactions.

Conversation:
{conversation_text}

Summary:
```

### Top-k retrieval

- **Configured:** `top_k: 3` in `configs/model_config.yaml` line 42
- **Used:** `self.retriever.retrieve(user_query, top_k=self.retriever.top_k)` in `main.py` line 124
- Effective results may be **fewer than 3** after cosine distance filtering (`distance >= 0.4` dropped)

---

## 4. MEMORY / CONVERSATION HANDLING

### Implementation layers

| Layer | Mechanism | Location |
|-------|-----------|----------|
| **Short-term (session UI)** | `st.session_state.messages` — list of `{role, content, timestamp}` | `app.py` lines 524–525, 751–809 |
| **In-process conversation** | `Memory.conversation_history` — list with role, content, timestamp, metadata | `core/memory.py` lines 39, 51–57 |
| **Long-term vector memory** | ChromaDB chunks via `store_conversation_chunk()` and summarization | `core/memory.py` lines 167–198, 127–135 |
| **Pipeline persistence** | `ChatbotPipeline` stored in `st.session_state.pipeline` | `app.py` lines 530–536 |

### Per-turn flow

1. User message added to in-memory history: `memory.add_message("user", ...)` (`main.py` line 201)
2. **Retrieval:** query embedded → ChromaDB top-3 search → distance filter (`main.py` line 124) — uses **current user query only**, not conversation history text
3. **Generation:** in-memory chat history + RAG context passed to LLM (`main.py` `_prepare_llm_input`, lines 130–144)
4. Assistant response added: `memory.add_message("assistant", ...)` (`main.py` line 150)
5. Last exchange stored to ChromaDB: `memory.store_conversation_chunk()` (`main.py` line 151)
6. Every 20 user messages: optional summarization → summary stored in ChromaDB, in-memory history trimmed to last 2 messages

### Where memory is used

| Step | In-memory history | ChromaDB (RAG) |
|------|-------------------|----------------|
| **Retrieval** | No | Yes — query is current user message |
| **Generation** | Yes — prior turns sent to LLM | Yes — retrieved chunks in system message / prompt |

Note: `Memory.get_rag_context()` exists (`core/memory.py` lines 62–86) but **`main.py` does not call it**; retrieval is done directly via `self.retriever.retrieve()` with equivalent context formatting.

### Clear behavior

- **Clear Chat** (`app.py` + `pipeline.clear_conversation()`): clears `st.session_state.messages` and in-memory `conversation_history` only
- **Does NOT** delete ChromaDB collection — old chunks remain retrievable after "clear"

---

## 5. APP STRUCTURE

**Confirmed: Streamlit application.**

| File | Purpose |
|------|---------|
| `app.py` | Main chat UI (landing page + chat interface) |
| `pages/dashboard.py` | MLflow observability dashboard (multi-page Streamlit) |

### Core flow (`app.py` → `main.py`)

1. **Init:** `st.set_page_config()` → inject global CSS → init `st.session_state` (`messages`, `chat_started`, `pipeline`)
2. **Pipeline init:** `ChatbotPipeline()` loads config, embedder, LLM, retriever, memory, observer
3. **Landing vs chat:** If `chat_started` is False → landing page; else → chat UI
4. **Sidebar:** message count, ChromaDB chunk count, LLM backend, Clear Chat, Dashboard link
5. **User input:** `st.chat_input()` → append user message to `session_state.messages`
6. **Generation:** `pipeline.process_query_stream(user_input)` yields token chunks
7. **Display:** HTML message bubbles updated during stream; typing indicator while waiting
8. **Backend pipeline (`process_query_stream`):**
   - Add user message to memory
   - Retrieve top-k chunks from ChromaDB
   - Build LLM messages/prompt with RAG + history
   - Stream LLM response
   - Store assistant message + conversation chunk to ChromaDB
   - Log metrics to MLflow via `ChatbotObserver`
9. **Dashboard:** separate page reads MLflow runs for charts and stats

---

## 6. SECRETS / CONFIG

### Configuration file

Primary runtime config: **`configs/model_config.yaml`** (loaded by `core/utils.py` `load_config()`)

### Secrets loading mechanisms

| Mechanism | Where | Variables |
|-----------|-------|-----------|
| **`.env` file** | Project root; loaded by `python-dotenv` | `load_dotenv()` in `core/utils.py` line 38 and `core/llm.py` line 12 |
| **Environment variables** | Read via `os.getenv()` in `core/llm.py` | `HF_API_TOKEN`, `OPENAI_API_KEY`, `DEEPSEEK_API_KEY` |
| **Streamlit secrets** | `app.py` lines 16–20 | Bridges `st.secrets` string values into `os.environ` (Streamlit Cloud) |
| **MLflow** | `core/observability.py` line 20 | `MLFLOW_TRACKING_URI` (default `./mlflow_runs`); `MLFLOW_ALLOW_FILE_STORE=true` set via `os.environ.setdefault` |

### `.env.example` keys (template only)

```
HF_API_TOKEN=...
OPENAI_API_KEY=...
DEEPSEEK_API_KEY=...
LLM_TYPE=huggingface
MODEL_PATH=models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
MLFLOW_TRACKING_URI=./mlflow_runs
```

**Note:** `LLM_TYPE` and `MODEL_PATH` in `.env.example` are **not read by application code** — backend selection comes from `configs/model_config.yaml` (`llm.type`, `local_llm.model_path`). Docker sets `LLM_TYPE` / `MODEL_PATH` env vars but the Python app does not consume them.

---

## 7. GAPS

Items to manually verify before building an eval harness:

1. **No static knowledge base** — Eval questions cannot assume fixed ground-truth documents; RAG only retrieves prior chat. First-turn queries always get zero chunks.

2. **Model identity confusion** — Config uses **Llama 3.1 8B** (HF) while README/UI/docs emphasize **Mistral 7B**. Confirm which model you intend to evaluate.

3. **`.env.example` vs code** — `LLM_TYPE` / `MODEL_PATH` env vars appear unused; only `model_config.yaml` controls backend. Easy to misconfigure.

4. **`CONTEXT.md` is stale** — Lists known issues (empty model path, no history to LLM, etc.) that appear fixed in current code. Do not rely on it for current behavior.

5. **Clear Chat does not reset ChromaDB** — Eval runs may retrieve chunks from previous sessions unless you manually delete `vectorstore/chroma_db/`.

6. **Non-deterministic / polluted memory** — Local ChromaDB may contain messy historical chunks (see sample doc 1 with garbled assistant output). Eval should use a clean vectorstore or account for contamination.

7. **Relevance score is not semantic** — MLflow logs `relevance_score = 1.0 if chunks_count > 0 else 0.0` (`core/observability.py` line 48). Not cosine similarity or LLM-judged relevance.

8. **`Memory.get_rag_context()` unused in main path** — Dead-ish API; main uses `retriever.retrieve()` directly. Behavior should be equivalent but divergent future edits possible.

9. **Summarization threshold** — Triggers at 20 **user** messages (`core/memory.py` line 96–97); summaries become new retrievable chunks with `type: "summary"`. Long eval sessions may change retrieval behavior mid-run.

10. **Distance threshold semantics** — Filter uses `distance >= 0.4` on Chroma cosine distance. Confirm Chroma version’s distance definition when interpreting retrieval quality metrics.

11. **Dual memory not synced on refresh** — `st.session_state.messages` (UI) and `Memory.conversation_history` (pipeline) are separate; page refresh resets UI but pipeline re-inits fresh memory while ChromaDB persists.

12. **HuggingFace Inference API availability** — `meta-llama/Llama-3.1-8B-Instruct` may require HF Pro/approved access; eval environment must have valid `HF_API_TOKEN` with model access.

13. **No document-upload RAG** — Despite README feature language, there is no file-ingestion path in code. Eval harness should treat this as **conversation-memory RAG**, not document QA.

14. **Docker vs local config mismatch** — Dockerfile defaults `LLM_TYPE=local`; `model_config.yaml` defaults `huggingface`. Container behavior depends on which config file is baked in, not Docker env alone.

---

*Audit completed read-only. ChromaDB sample queried locally for illustration; counts and samples will vary per deployment.*
