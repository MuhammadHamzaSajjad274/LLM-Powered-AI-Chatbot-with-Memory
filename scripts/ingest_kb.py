#!/usr/bin/env python3
"""
Ingest FlowBoard knowledge-base markdown files into ChromaDB.

Standalone script — also provides run_kb_ingestion() for automatic startup ingestion.

Manual script idempotency: clear + rebuild on every run.
Startup auto-ingestion: populate only when collection is empty (no clear).
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure project root is on sys.path when run as a script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.embeddings import Embedder
from core.kb_retriever import KBRetriever
from core.utils import ensure_directory, setup_logging

logger = logging.getLogger(__name__)

KB_DIR = PROJECT_ROOT / "data" / "kb"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def run_kb_ingestion(
    embedder: Optional[Embedder] = None,
    kb_retriever: Optional[KBRetriever] = None,
    *,
    force_rebuild: bool = False,
    kb_dir: Optional[Path] = None,
    embedding_model: str = EMBEDDING_MODEL,
) -> Dict[str, int]:
    """
    Read markdown from data/kb/, chunk, embed, and load into the KB collection.

    Args:
        embedder: Optional shared Embedder instance (created if omitted).
        kb_retriever: Optional KBRetriever instance (created if omitted).
        force_rebuild: If True, clear existing collection before ingesting
            (used by manual script runs). If False, append into current collection.
        kb_dir: Override path to markdown source directory.
        embedding_model: Model name when creating a new Embedder.

    Returns:
        Dict with keys: files_processed, chunks_created, collection_count.

    Raises:
        FileNotFoundError: If kb_dir is missing or contains no .md files.
    """
    source_dir = kb_dir or KB_DIR
    ensure_directory("vectorstore/chroma_db_kb")

    if not source_dir.is_dir():
        raise FileNotFoundError(f"Knowledge-base directory not found: {source_dir}")

    md_files = sorted(source_dir.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No .md files found in {source_dir}")

    if embedder is None:
        embedder = Embedder(model_name=embedding_model, device="cpu")
    if kb_retriever is None:
        kb_retriever = KBRetriever(embedder=embedder)

    if force_rebuild and kb_retriever.get_collection_count() > 0:
        kb_retriever.clear_collection()
        logger.info("KB collection cleared for rebuild")

    all_texts: list[str] = []
    all_metadatas: list[Dict[str, Any]] = []
    all_ids: list[str] = []

    for md_file in md_files:
        chunks = kb_retriever.chunk_markdown_file(md_file)
        for chunk_text, metadata in chunks:
            all_texts.append(chunk_text)
            all_metadatas.append(metadata)
            all_ids.append(f"{md_file.stem}_chunk_{metadata['chunk_index']}")

    if all_texts:
        kb_retriever.add_documents(
            texts=all_texts,
            metadatas=all_metadatas,
            ids=all_ids,
        )

    stats = {
        "files_processed": len(md_files),
        "chunks_created": len(all_texts),
        "collection_count": kb_retriever.get_collection_count(),
    }
    return stats


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
    else:
        print("Existing chunks  : 0 (fresh ingest)")

    print()
    for md_file in md_files:
        preview_count = len(kb.chunk_markdown_file(md_file))
        print(f"  {md_file.name:40s} -> {preview_count} chunk(s)")

    print()
    print("Adding chunks to ChromaDB...")
    stats = run_kb_ingestion(
        embedder=embedder,
        kb_retriever=kb,
        force_rebuild=True,
    )

    print()
    print("=" * 50)
    print("Ingestion complete")
    print(f"  Files processed : {stats['files_processed']}")
    print(f"  Chunks created  : {stats['chunks_created']}")
    print(f"  Collection count: {stats['collection_count']}")
    print("=" * 50)


if __name__ == "__main__":
    main()
