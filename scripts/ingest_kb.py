#!/usr/bin/env python3
"""
Ingest FlowBoard knowledge-base markdown files into ChromaDB.

Standalone script — not wired into the Streamlit app.

Idempotency: uses clear+rebuild — deletes the flowboard_kb collection
and re-ingests all files from data/kb/ on every run, so running twice
produces the same result with no duplicate chunks.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path when run as a script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.embeddings import Embedder
from core.kb_retriever import KBRetriever
from core.utils import ensure_directory, setup_logging

KB_DIR = PROJECT_ROOT / "data" / "kb"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def main() -> None:
    setup_logging()
    ensure_directory("vectorstore/chroma_db_kb")

    if not KB_DIR.is_dir():
        print(f"ERROR: Knowledge-base directory not found: {KB_DIR}")
        sys.exit(1)

    md_files = sorted(KB_DIR.glob("*.md"))
    if not md_files:
        print(f"ERROR: No .md files found in {KB_DIR}")
        sys.exit(1)

    print("FlowBoard KB Ingestion")
    print("=" * 50)
    print(f"Source directory : {KB_DIR}")
    print(f"Embedding model  : {EMBEDDING_MODEL}")
    print(f"Collection       : flowboard_kb")
    print(f"Persist path     : vectorstore/chroma_db_kb")
    print(f"Strategy         : clear + rebuild (idempotent)")
    print()

    embedder = Embedder(model_name=EMBEDDING_MODEL, device="cpu")
    kb = KBRetriever(embedder=embedder)

    existing_count = kb.get_collection_count()
    if existing_count > 0:
        print(f"Existing chunks  : {existing_count} (will be cleared)")
        kb.clear_collection()
        print("Collection cleared and recreated.")
    else:
        print("Existing chunks  : 0 (fresh ingest)")

    print()
    total_chunks = 0
    all_texts = []
    all_metadatas = []
    all_ids = []

    for md_file in md_files:
        chunks = kb.chunk_markdown_file(md_file)
        file_chunk_count = len(chunks)
        total_chunks += file_chunk_count
        print(f"  {md_file.name:40s} -> {file_chunk_count} chunk(s)")

        for chunk_text, metadata in chunks:
            stem = md_file.stem
            chunk_idx = metadata["chunk_index"]
            all_texts.append(chunk_text)
            all_metadatas.append(metadata)
            all_ids.append(f"{stem}_chunk_{chunk_idx}")

    print()
    print(f"Adding {total_chunks} chunks to ChromaDB...")
    kb.add_documents(texts=all_texts, metadatas=all_metadatas, ids=all_ids)

    final_count = kb.get_collection_count()
    print()
    print("=" * 50)
    print("Ingestion complete")
    print(f"  Files processed : {len(md_files)}")
    print(f"  Chunks created  : {total_chunks}")
    print(f"  Collection count: {final_count}")
    print("=" * 50)


if __name__ == "__main__":
    main()
