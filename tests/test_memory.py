"""
Unit tests for memory addition, retrieval, and summarization.
"""

import unittest
from unittest.mock import Mock

from core.memory import Memory


class TestMemory(unittest.TestCase):
    """Test cases for Memory class."""

    def setUp(self):
        """Set up test fixtures with mocked dependencies."""
        self.mock_retriever = Mock()
        self.mock_retriever.top_k = 3
        self.mock_retriever.retrieve.return_value = []
        self.mock_llm = Mock()
        self.memory = Memory(
            retriever=self.mock_retriever,
            llm=self.mock_llm,
            summarization_threshold=5
        )

    def test_store_conversation_chunk_stores_only_two_messages(self):
        """store_conversation_chunk() stores only the last user+assistant exchange."""
        self.memory.add_message("user", "first question")
        self.memory.add_message("assistant", "first answer")
        self.memory.add_message("user", "second question")
        self.memory.add_message("assistant", "second answer")

        self.memory.store_conversation_chunk()

        self.mock_retriever.add_documents.assert_called_once()
        stored_text = self.mock_retriever.add_documents.call_args.kwargs["texts"][0]
        self.assertIn("User: second question", stored_text)
        self.assertIn("Assistant: second answer", stored_text)
        self.assertNotIn("first question", stored_text)
        self.assertNotIn("first answer", stored_text)

    def test_get_conversation_messages_returns_correct_format(self):
        """get_conversation_messages() returns role/content dicts."""
        self.memory.add_message("user", "Hello")
        self.memory.add_message("assistant", "Hi there!")

        messages = self.memory.get_conversation_messages()

        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0], {"role": "user", "content": "Hello"})
        self.assertEqual(messages[1], {"role": "assistant", "content": "Hi there!"})
        self.assertNotIn("timestamp", messages[0])
        self.assertNotIn("metadata", messages[0])

    def test_get_rag_context_returns_empty_when_no_history(self):
        """get_rag_context() returns empty string when retriever finds nothing."""
        self.mock_retriever.retrieve.return_value = []

        context = self.memory.get_rag_context("Tell me about Python")

        self.assertEqual(context, "")
        self.mock_retriever.retrieve.assert_called_once_with(
            "Tell me about Python", top_k=3
        )

    def test_add_message(self):
        """Test adding messages to memory."""
        self.memory.add_message("user", "Hello")
        self.memory.add_message("assistant", "Hi there!")

        history = self.memory.get_conversation_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello")

    def test_clear_conversation(self):
        """Test clearing conversation history and ChromaDB memory collection."""
        self.memory.add_message("user", "Test")
        self.memory.add_message("assistant", "Response")

        self.memory.clear_conversation_history()

        self.assertEqual(len(self.memory.get_conversation_history()), 0)
        self.assertEqual(self.memory.message_count, 0)
        self.mock_retriever.clear_collection.assert_called_once()


if __name__ == "__main__":
    unittest.main()
