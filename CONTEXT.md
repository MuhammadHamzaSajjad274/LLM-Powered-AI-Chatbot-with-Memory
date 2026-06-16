# Project: LLM-Powered AI Chatbot with Memory

## What this is
A locally-hosted AI chatbot with long-term memory built with Streamlit, ChromaDB,
and Mistral 7B (GGUF via llama-cpp-python). Supports three LLM backends:
local (Mistral 7B), OpenAI, and Deepseek.

## Architecture
- app.py — Streamlit UI, session state, chat rendering
- main.py — ChatbotPipeline class, orchestrates all components
- core/llm.py — LLMBase abstract class, LocalLLM, OpenAILLM, DeepseekLLM, LLMModel wrapper
- core/memory.py — Memory class, conversation history, RAG context retrieval, summarization
- core/retriever.py — Retriever class, ChromaDB queries, add_documents, top-k search
- core/embeddings.py — Embedder class using sentence-transformers/all-MiniLM-L6-v2
- core/utils.py — load_config, setup_logging, ensure_directory
- configs/model_config.yaml — all runtime configuration (LLM type, paths, thresholds)

## Known issues to fix (in order)
1. model_config.yaml has model_path="" — must point to the actual .gguf file
2. LocalLLM.generate() sends raw prompt without Mistral [INST] chat template
3. store_conversation_chunk() stores entire history every turn (should store last exchange only)
4. LLM receives no conversation history — each turn is stateless from the model's perspective
5. ctransformers is the primary backend but is abandoned; switch to llama-cpp-python
6. ChromaDB Settings() usage is outdated (deprecation warnings in newer versions)
7. No relevance filtering on retrieved chunks (all top-k returned regardless of distance)
8. No .env support — secrets are hardcoded or raw env vars
9. Docker VOLUME not defined — model file can't be mounted

## Stack
Python 3.10+, Streamlit, ChromaDB, sentence-transformers, llama-cpp-python,
openai SDK, PyYAML, pytest (tests exist but need filling in)

## Development phases
Phase 1: Fix all broken issues listed above
Phase 2: Add streaming, relevance filtering, .env support, fix Docker, add tests
Phase 3: Add one major feature (document upload RAG, multi-session, or MLflow observability)

## Constraints
- Keep changes surgical — one issue at a time, no scope creep
- Always preserve the existing module structure
- Test manually after each fix before moving to the next