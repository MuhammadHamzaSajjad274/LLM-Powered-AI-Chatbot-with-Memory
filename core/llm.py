"""
LLM wrapper class for managing different LLM providers (Local, OpenAI, Deepseek).
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Iterator
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

logger = logging.getLogger(__name__)


class LLMBase(ABC):
    """Base class for LLM implementations."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the LLM."""
        pass


class LocalLLM(LLMBase):
    """Local LLM implementation using ctransformers or llama-cpp-python."""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        model_type: str = "mistral",
        temperature: float = 0.7,
        max_tokens: int = 512,
        gpu_layers: int = 0
    ):
        """
        Initialize local LLM.
        
        Args:
            model_path: Path to the model file (.gguf)
            model_type: Model architecture type
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            gpu_layers: Number of layers to offload to GPU
        """
        self.model_path = model_path
        self.model_type = model_type
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.gpu_layers = gpu_layers
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the local model."""
        model_path_str = self.model_path
        if not model_path_str or not str(model_path_str).strip():
            raise FileNotFoundError(
                f"Model file not found at {model_path_str}. Please place your .gguf file "
                "in the models/ folder and update model_path in configs/model_config.yaml"
            )

        model_path = Path(model_path_str)
        if not model_path.is_absolute():
            model_path = Path(__file__).parent.parent / model_path

        if not model_path.is_file():
            raise FileNotFoundError(
                f"Model file not found at {model_path_str}. Please place your .gguf file "
                "in the models/ folder and update model_path in configs/model_config.yaml"
            )

        resolved_path = str(model_path)

        try:
            # Try llama-cpp-python first
            try:
                from llama_cpp import Llama
                logger.info("Using llama-cpp-python for local LLM")
                self.model = Llama(
                    model_path=resolved_path,
                    n_gpu_layers=self.gpu_layers,
                    verbose=False
                )
            except ImportError:
                # Fallback to ctransformers
                try:
                    from ctransformers import AutoModelForCausalLM
                    logger.info("Using ctransformers for local LLM")
                    self.model = AutoModelForCausalLM.from_pretrained(
                        resolved_path,
                        model_type=self.model_type,
                        gpu_layers=self.gpu_layers
                    )
                except ImportError:
                    raise ImportError(
                        "Neither ctransformers nor llama-cpp-python is installed. "
                        "Install one of them: pip install ctransformers or pip install llama-cpp-python"
                    )

            logger.info("Local LLM model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load local LLM: {e}")
            raise
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using the local model.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        
        try:
            # Check if using ctransformers
            if hasattr(self.model, "generate"):
                # ctransformers API
                response = self.model(
                    formatted_prompt,
                    temperature=temperature,
                    max_new_tokens=max_tokens
                )
                return response
            else:
                # llama-cpp-python API
                response = self.model(
                    formatted_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    echo=False
                )
                return response["choices"][0]["text"]
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream a response using the local model, yielding token chunks.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Yields:
            Generated text chunks as they arrive
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")

        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"

        try:
            if hasattr(self.model, "generate"):
                response = self.model(
                    formatted_prompt,
                    temperature=temperature,
                    max_new_tokens=max_tokens,
                    stream=True
                )
                for chunk in response:
                    if chunk:
                        yield chunk
            else:
                stream = self.model(
                    formatted_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    echo=False,
                    stream=True
                )
                for chunk in stream:
                    if not chunk.get("choices"):
                        continue
                    text = chunk["choices"][0].get("text", "")
                    if text:
                        yield text
        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            raise


class OpenAILLM(LLMBase):
    """OpenAI API LLM implementation."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        """
        Initialize OpenAI LLM.
        
        Args:
            api_key: OpenAI API key
            model_name: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
        
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using OpenAI API.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {e}")
            raise

    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream a response using OpenAI API, yielding token chunks.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Yields:
            Generated text chunks as they arrive
        """
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            logger.error(f"Error streaming response with OpenAI: {e}")
            raise


class DeepseekLLM(LLMBase):
    """Deepseek API LLM implementation."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        """
        Initialize Deepseek LLM.
        
        Args:
            api_key: Deepseek API key
            model_name: Model name to use
            base_url: API base URL
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        except ImportError:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
        
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using Deepseek API.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response with Deepseek: {e}")
            raise

    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """Stream a response using Deepseek API, yielding token chunks."""
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        try:
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            logger.error(f"Error streaming response with Deepseek: {e}")
            raise


class HuggingFaceLLM(LLMBase):
    """HuggingFace Inference API LLM implementation."""

    def __init__(
        self,
        api_token: Optional[str] = None,
        model_name: str = "mistralai/Mistral-7B-Instruct-v0.2",
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        """
        Initialize HuggingFace Inference API LLM.

        Args:
            api_token: HuggingFace API token
            model_name: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        try:
            from huggingface_hub import InferenceClient
            self.client = InferenceClient(model=model_name, token=api_token)
        except ImportError:
            raise ImportError(
                "huggingface_hub library not installed. Install with: pip install huggingface_hub"
            )

        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using HuggingFace Inference API.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            Generated text response
        """
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        try:
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response with HuggingFace: {e}")
            raise

    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream a response using HuggingFace Inference API, yielding tokens.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Yields:
            Generated tokens as they arrive
        """
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        try:
            stream = self.client.chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            logger.error(f"Error streaming response with HuggingFace: {e}")
            raise


class LLMModel:
    """
    Main LLM wrapper class that manages different LLM providers.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize LLM model based on configuration.
        
        Args:
            config: Configuration dictionary containing LLM settings
        """
        self.config = config
        self.llm_type = config.get("llm", {}).get("type", "local")
        self.llm: Optional[LLMBase] = None
        self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """Initialize the appropriate LLM based on configuration."""
        llm_config = self.config.get("llm", {})
        temperature = llm_config.get("temperature", 0.7)
        max_tokens = llm_config.get("max_tokens", 512)
        
        if self.llm_type == "local":
            local_config = self.config.get("local_llm", {})
            self.llm = LocalLLM(
                model_path=local_config.get("model_path"),
                model_type=local_config.get("model_type", "mistral"),
                temperature=temperature,
                max_tokens=max_tokens,
                gpu_layers=local_config.get("gpu_layers", 0)
            )
        elif self.llm_type == "openai":
            openai_config = self.config.get("openai", {})
            api_key = os.getenv("OPENAI_API_KEY") or openai_config.get("api_key")
            if not api_key:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            self.llm = OpenAILLM(
                api_key=api_key,
                model_name=openai_config.get("model_name", "gpt-3.5-turbo"),
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif self.llm_type == "deepseek":
            deepseek_config = self.config.get("deepseek", {})
            api_key = os.getenv("DEEPSEEK_API_KEY") or deepseek_config.get("api_key")
            if not api_key:
                raise ValueError("Deepseek API key not found. Set DEEPSEEK_API_KEY environment variable.")
            self.llm = DeepseekLLM(
                api_key=api_key,
                model_name=deepseek_config.get("model_name", "deepseek-chat"),
                base_url=deepseek_config.get("base_url", "https://api.deepseek.com"),
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif self.llm_type == "huggingface":
            hf_config = self.config.get("huggingface", {})
            api_token = (os.getenv("HF_API_TOKEN") or hf_config.get("api_token") or "").strip()
            if not api_token or api_token == "your-hf-token-here":
                raise ValueError(
                    "HuggingFace API token not found. Set HF_API_TOKEN in your .env file "
                    "(get a token at https://huggingface.co/settings/tokens)."
                )
            self.llm = HuggingFaceLLM(
                api_token=api_token,
                model_name=hf_config.get("model_name", "mistralai/Mistral-7B-Instruct-v0.2"),
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            raise ValueError(f"Unknown LLM type: {self.llm_type}")
        
        logger.info(f"Initialized LLM: {self.llm_type}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using the configured LLM.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        if self.llm is None:
            raise RuntimeError("LLM not initialized")
        return self.llm.generate(prompt, **kwargs)

    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """
        Stream a response using the configured LLM.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Yields:
            Generated text chunks as they arrive
        """
        if self.llm is None:
            raise RuntimeError("LLM not initialized")
        if hasattr(self.llm, "stream_generate"):
            yield from self.llm.stream_generate(prompt, **kwargs)
        else:
            yield self.llm.generate(prompt, **kwargs)

    def get_type(self) -> str:
        """Get the current LLM type."""
        return self.llm_type


