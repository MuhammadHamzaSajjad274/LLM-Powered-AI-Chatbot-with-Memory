"""
Unit tests for Retriever vector search and distance filtering.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

from core.retriever import Retriever


class TestRetriever(unittest.TestCase):
    """Test cases for Retriever class."""

    def setUp(self):
        """Set up a Retriever with mocked ChromaDB and embedder."""
        self.mock_embedder = Mock()
        self.mock_embedder.embed_query.return_value = [0.1, 0.2, 0.3]
        self.mock_embedder.embed_documents.return_value = [[0.1, 0.2, 0.3]]

        self.mock_collection = Mock()
        self.mock_collection.count.return_value = 3

        self.mock_client = Mock()
        self.mock_client.get_collection.return_value = self.mock_collection

        patcher = patch("core.retriever.chromadb.PersistentClient", return_value=self.mock_client)
        self.addCleanup(patcher.stop)
        patcher.start()

        self.retriever = Retriever(
            collection_name="test_collection",
            persist_directory="test_db",
            embedder=self.mock_embedder,
            top_k=3
        )

    def test_retrieve_filters_results_with_distance_gte_0_4(self):
        """retrieve() excludes chunks with cosine distance >= 0.4."""
        self.mock_collection.query.return_value = {
            "ids": [["doc1", "doc2", "doc3"]],
            "documents": [["relevant", "irrelevant", "borderline"]],
            "metadatas": [[{}, {}, {}]],
            "distances": [[0.2, 0.5, 0.39]]
        }

        results = self.retriever.retrieve("test query")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "doc1")
        self.assertEqual(results[0]["distance"], 0.2)
        self.assertEqual(results[1]["id"], "doc3")
        self.assertEqual(results[1]["distance"], 0.39)
        self.mock_collection.query.assert_called_once_with(
            query_embeddings=[[0.1, 0.2, 0.3]],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )

    def test_retrieve_returns_empty_when_nothing_passes_threshold(self):
        """retrieve() returns empty list when all distances are >= 0.4."""
        self.mock_collection.query.return_value = {
            "ids": [["doc1", "doc2"]],
            "documents": [["a", "b"]],
            "metadatas": [[{}, {}]],
            "distances": [[0.4, 0.9]]
        }

        results = self.retriever.retrieve("test query")

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
