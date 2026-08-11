"""
Knowledge-base retriever for static FlowBoard documentation in ChromaDB.

Separate from core/retriever.py (conversational memory). Uses its own
collection and persist directory so long_term_chat_memory is never touched.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import chromadb

logger = logging.getLogger(__name__)

DEFAULT_COLLECTION_NAME = "flowboard_kb"
DEFAULT_PERSIST_DIRECTORY = "vectorstore/chroma_db_kb"
DEFAULT_KB_DISTANCE_THRESHOLD = 0.55
TARGET_MIN_WORDS = 200
TARGET_MAX_WORDS = 300


class KBRetriever:
    """Vector retriever for static markdown knowledge-base chunks."""

    def __init__(
        self,
        embedder,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        persist_directory: str = DEFAULT_PERSIST_DIRECTORY,
        top_k: int = 3,
        kb_distance_threshold: float = DEFAULT_KB_DISTANCE_THRESHOLD,
    ):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedder = embedder
        self.top_k = top_k
        self.kb_distance_threshold = kb_distance_threshold

        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self._get_or_create_collection()
        logger.info(
            "KBRetriever initialized: collection=%s, path=%s, top_k=%s, threshold=%s",
            collection_name,
            persist_directory,
            top_k,
            kb_distance_threshold,
        )

    def _get_or_create_collection(self):
        """Get existing collection or create a new one."""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            logger.info("Retrieved existing KB collection: %s", self.collection_name)
        except Exception:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("Created KB collection: %s", self.collection_name)
        return collection

    def clear_collection(self) -> None:
        """Delete and recreate the KB collection (used before full re-ingestion)."""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info("Deleted KB collection: %s", self.collection_name)
        except Exception:
            pass
        self.collection = self._get_or_create_collection()

    @staticmethod
    def chunk_markdown(text: str, source_file: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Split markdown into passages of roughly 200-300 words.

        Uses header boundaries first, then paragraph merging/splitting.
        """
        text = text.strip()
        if not text:
            return []

        sections = re.split(r"(?=^#{1,3} .+$)", text, flags=re.MULTILINE)
        raw_chunks: List[str] = []

        for section in sections:
            section = section.strip()
            if not section:
                continue
            word_count = len(section.split())
            if word_count <= TARGET_MAX_WORDS:
                raw_chunks.append(section)
                continue

            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", section) if p.strip()]
            current_parts: List[str] = []
            current_words = 0

            for para in paragraphs:
                para_words = len(para.split())
                if current_words + para_words > TARGET_MAX_WORDS and current_parts:
                    raw_chunks.append("\n\n".join(current_parts))
                    current_parts = [para]
                    current_words = para_words
                else:
                    current_parts.append(para)
                    current_words += para_words

            if current_parts:
                raw_chunks.append("\n\n".join(current_parts))

        merged: List[str] = []
        buffer = ""
        buffer_words = 0
        for chunk in raw_chunks:
            chunk_words = len(chunk.split())
            if buffer and buffer_words + chunk_words <= TARGET_MIN_WORDS:
                buffer = f"{buffer}\n\n{chunk}"
                buffer_words += chunk_words
            elif buffer:
                merged.append(buffer)
                buffer = chunk
                buffer_words = chunk_words
            else:
                buffer = chunk
                buffer_words = chunk_words
        if buffer:
            merged.append(buffer)

        results: List[Tuple[str, Dict[str, Any]]] = []
        for idx, chunk_text in enumerate(merged):
            header_match = re.search(r"^#{1,3}\s+(.+)$", chunk_text, re.MULTILINE)
            title = header_match.group(1).strip() if header_match else source_file
            results.append(
                (
                    chunk_text,
                    {
                        "source_file": source_file,
                        "chunk_index": idx,
                        "title": title,
                        "type": "kb_chunk",
                    },
                )
            )
        return results

    def chunk_markdown_file(self, file_path: Path) -> List[Tuple[str, Dict[str, Any]]]:
        """Read a markdown file and return chunked passages with metadata."""
        text = file_path.read_text(encoding="utf-8")
        return self.chunk_markdown(text, source_file=file_path.name)

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve top-k KB passages for a query.

        Mirrors core/retriever.py interface and cosine distance filtering.
        """
        if top_k is None:
            top_k = self.top_k

        count = self.collection.count()
        if count == 0:
            return []

        query_embedding = self.embedder.embed_query(query)

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, count),
                include=["documents", "metadatas", "distances"],
            )

            retrieved_docs: List[Dict[str, Any]] = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    distance = results["distances"][0][i] if results["distances"] else None
                    if distance is not None and distance >= self.kb_distance_threshold:
                        continue
                    retrieved_docs.append(
                        {
                            "id": results["ids"][0][i],
                            "text": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i]
                            if results["metadatas"]
                            else {},
                            "distance": distance,
                        }
                    )

            logger.debug("KB retrieved %d documents for query", len(retrieved_docs))
            return retrieved_docs

        except Exception as e:
            logger.error("Error retrieving KB documents: %s", e)
            return []

    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Add document chunks to the KB collection."""
        if not texts:
            return

        embeddings = self.embedder.embed_documents(texts)

        if metadatas is None:
            metadatas = [{}] * len(texts)

        if ids is None:
            current_count = self.collection.count()
            ids = [f"kb_doc_{current_count + i}" for i in range(len(texts))]

        try:
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info("Added %d KB documents to collection", len(texts))
        except Exception as e:
            logger.error("Error adding KB documents: %s", e)
            raise

    def get_collection_count(self) -> int:
        """Return the number of documents in the KB collection."""
        return self.collection.count()
