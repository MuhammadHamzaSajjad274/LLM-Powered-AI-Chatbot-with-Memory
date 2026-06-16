"""
Unit tests for LLM selection and basic generation.
"""

import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from core.llm import LLMModel, LocalLLM, HuggingFaceLLM


class TestLLM(unittest.TestCase):
    """Test cases for LLM classes."""

    def test_huggingface_llm_raises_error_when_token_missing(self):
        """HuggingFaceLLM initialization via LLMModel fails without HF_API_TOKEN."""
        config = {
            "llm": {"type": "huggingface", "temperature": 0.7, "max_tokens": 100},
            "huggingface": {
                "model_name": "mistralai/Mistral-7B-Instruct-v0.2",
                "api_token": ""
            }
        }

        original_token = os.environ.pop("HF_API_TOKEN", None)
        try:
            with self.assertRaises(ValueError) as ctx:
                LLMModel(config)
            self.assertIn("HuggingFace API token not found", str(ctx.exception))
        finally:
            if original_token is not None:
                os.environ["HF_API_TOKEN"] = original_token

    def test_local_llm_raises_error_when_model_file_missing(self):
        """LocalLLM raises FileNotFoundError when the model file does not exist."""
        missing_path = "models/nonexistent-model.gguf"
        resolved = Path(__file__).parent.parent / missing_path
        self.assertFalse(resolved.is_file())

        with self.assertRaises(FileNotFoundError) as ctx:
            LocalLLM(model_path=missing_path, model_type="mistral")

        self.assertIn("Model file not found", str(ctx.exception))

    @patch("core.llm.Path.is_file", return_value=True)
    @patch("llama_cpp.Llama")
    def test_local_llm_generate_with_mocked_model(self, mock_llama_cls, _mock_is_file):
        """LocalLLM.generate() works with a mocked llama-cpp model."""
        class FakeLlamaModel:
            def __call__(self, *args, **kwargs):
                return {"choices": [{"text": "Hello from local LLM"}]}

        mock_llama_cls.return_value = FakeLlamaModel()

        llm = LocalLLM(
            model_path="models/test.gguf",
            model_type="mistral",
            temperature=0.7,
            max_tokens=50
        )
        response = llm.generate("Hi")

        self.assertEqual(response, "Hello from local LLM")
        mock_llama_cls.assert_called_once()

    @patch("huggingface_hub.InferenceClient")
    def test_huggingface_llm_generate_with_mocked_client(self, mock_client_cls):
        """HuggingFaceLLM.generate() works with a mocked InferenceClient."""
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello from HuggingFace"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat_completion.return_value = mock_response
        mock_client_cls.return_value = mock_client

        llm = HuggingFaceLLM(api_token="hf_test_token")
        response = llm.generate("Hi")

        self.assertEqual(response, "Hello from HuggingFace")
        mock_client.chat_completion.assert_called_once()

    def test_llm_model_invalid_type(self):
        """Test that invalid LLM type raises an error."""
        invalid_config = {
            "llm": {"type": "invalid", "temperature": 0.7, "max_tokens": 100}
        }

        with self.assertRaises(ValueError):
            LLMModel(invalid_config)


if __name__ == "__main__":
    unittest.main()
