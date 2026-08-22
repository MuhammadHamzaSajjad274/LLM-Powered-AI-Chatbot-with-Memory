"""
Embeddings class for generating vector representations of text.
"""

import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class Embedder:
    """
    Class for generating embeddings using sentence-transformers models.
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu"
    ):
        """
        Initialize the Embedder with a sentence-transformers model.
        
        Args:
            model_name: Name of the sentence-transformers model
            device: Device to run the model on ("cpu" or "cuda")
        """
        self.model_name = model_name
        self.device = device
        self.model: Optional[SentenceTransformer] = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the sentence-transformers model."""
        try:
            logger.info(f"Loading embeddings model: {self.model_name}")
            # low_cpu_mem_usage=False avoids meta-tensor load failures on torch 2.4+
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
                model_kwargs={"low_cpu_mem_usage": False},
            )
            logger.info(f"Embeddings model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load embeddings model: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of float values representing the embedding vector
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call _load_model() first.")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors (each is a list of floats)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call _load_model() first.")
        
        if not texts:
            return []
        
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Dimension of the embedding vectors
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call _load_model() first.")
        
        # Get dimension by encoding a dummy text
        dummy_embedding = self.model.encode("dummy", convert_to_numpy=True)
        return len(dummy_embedding)


