"""
Unit tests for the embedding generation and shape validation.
"""

import unittest
import numpy as np

from core.embeddings import Embedder


class TestEmbeddings(unittest.TestCase):
    """Test cases for Embedder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.embedder = Embedder()
    
    def test_embed_query(self):
        """Test embedding generation for a single query."""
        text = "This is a test query"
        embedding = self.embedder.embed_query(text)
        
        # Check that embedding is a list
        self.assertIsInstance(embedding, list)
        
        # Check that all elements are floats
        self.assertTrue(all(isinstance(x, (int, float)) for x in embedding))
        
        # Check that embedding is not empty
        self.assertGreater(len(embedding), 0)
    
    def test_embed_documents(self):
        """Test embedding generation for multiple documents."""
        texts = [
            "First document",
            "Second document",
            "Third document"
        ]
        embeddings = self.embedder.embed_documents(texts)
        
        # Check that embeddings is a list
        self.assertIsInstance(embeddings, list)
        
        # Check that we have the same number of embeddings as documents
        self.assertEqual(len(embeddings), len(texts))
        
        # Check that each embedding is a list of floats
        for embedding in embeddings:
            self.assertIsInstance(embedding, list)
            self.assertTrue(all(isinstance(x, (int, float)) for x in embedding))
    
    def test_embedding_dimension(self):
        """Test that embeddings have consistent dimensions."""
        text1 = "First text"
        text2 = "Second text with different length"
        
        embedding1 = self.embedder.embed_query(text1)
        embedding2 = self.embedder.embed_query(text2)
        
        # Check that both embeddings have the same dimension
        self.assertEqual(len(embedding1), len(embedding2))
        
        # Check using the get_embedding_dimension method
        dimension = self.embedder.get_embedding_dimension()
        self.assertEqual(len(embedding1), dimension)
        self.assertEqual(len(embedding2), dimension)
    
    def test_empty_documents(self):
        """Test handling of empty document list."""
        embeddings = self.embedder.embed_documents([])
        self.assertEqual(embeddings, [])
    
    def test_embedding_consistency(self):
        """Test that same text produces same embedding."""
        text = "Consistent text"
        embedding1 = self.embedder.embed_query(text)
        embedding2 = self.embedder.embed_query(text)
        
        # Embeddings should be identical (or very close due to floating point)
        np.testing.assert_array_almost_equal(embedding1, embedding2, decimal=5)


if __name__ == "__main__":
    unittest.main()


