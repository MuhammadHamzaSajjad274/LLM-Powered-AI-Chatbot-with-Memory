"""
Main pipeline entry point for the LLM-Powered AI Chatbot with Long-Term Memory.
Initializes core classes and orchestrates the RAG process.
"""

import logging
import time
from typing import Optional, List, Dict, Iterator

from core.utils import load_config, setup_logging, ensure_directory
from core.embeddings import Embedder
from core.llm import LLMModel
from core.retriever import Retriever
from core.kb_retriever import KBRetriever, DEFAULT_KB_DISTANCE_THRESHOLD
from core.memory import Memory
from core.observability import ChatbotObserver

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)


class ChatbotPipeline:
    """
    Main pipeline class that orchestrates the RAG process.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the chatbot pipeline.
        
        Args:
            config_path: Optional path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)
        logger.info("Configuration loaded")
        
        # Initialize components
        self._initialize_components()
        logger.info("Chatbot pipeline initialized")
    
    def _initialize_components(self) -> None:
        """Initialize all core components."""
        # Ensure vectorstore directory exists
        vectorstore_path = self.config.get("memory", {}).get("vectorstore_path", "vectorstore/chroma_db")
        ensure_directory(vectorstore_path)
        
        # Initialize embeddings
        embeddings_config = self.config.get("embeddings", {})
        self.embedder = Embedder(
            model_name=embeddings_config.get("model_name", "sentence-transformers/all-MiniLM-L6-v2"),
            device=embeddings_config.get("device", "cpu")
        )
        
        # Initialize LLM
        self.llm = LLMModel(self.config)
        
        # Initialize retriever
        memory_config = self.config.get("memory", {})
        self.retriever = Retriever(
            collection_name=memory_config.get("collection_name", "long_term_chat_memory"),
            persist_directory=memory_config.get("vectorstore_path", "vectorstore/chroma_db"),
            embedder=self.embedder,
            top_k=memory_config.get("top_k", 3)
        )
        
        # Initialize memory
        self.memory = Memory(
            retriever=self.retriever,
            llm=self.llm,
            summarization_threshold=memory_config.get("summarization_threshold", 20)
        )

        kb_config = self.config.get("kb", {})
        self.kb_retriever = KBRetriever(
            embedder=self.embedder,
            top_k=kb_config.get("top_k", 3),
            kb_distance_threshold=kb_config.get("distance_threshold", DEFAULT_KB_DISTANCE_THRESHOLD),
        )
        self.last_query_retrieval = {"memory": 0, "kb": 0}
        self.observer = ChatbotObserver()
    
    def _build_prompt(self, user_query: str, rag_context: str) -> str:
        """Build the LLM prompt with optional RAG context."""
        if rag_context:
            return f"""Based on the following context, please answer the user's question.

{rag_context}

Current question: {user_query}

Please provide a helpful and accurate response:"""
        return user_query

    @staticmethod
    def _format_rag_context(
        kb_chunks: List[Dict],
        memory_chunks: List[Dict],
    ) -> str:
        """Combine KB and memory retrieval results with distinct labels."""
        sections: List[str] = []
        if kb_chunks:
            kb_parts = [doc["text"] for doc in kb_chunks]
            sections.append(
                "Relevant information from the knowledge base:\n" + "\n\n".join(kb_parts)
            )
        if memory_chunks:
            mem_parts = [f"Previous conversation: {doc['text']}" for doc in memory_chunks]
            sections.append(
                "Relevant information from previous conversations:\n" + "\n\n".join(mem_parts)
            )
        return "\n\n".join(sections)

    @staticmethod
    def _format_history_as_text(messages: List[Dict[str, str]]) -> str:
        """Format conversation messages as plain text for local LLM prompts."""
        parts = []
        for msg in messages:
            parts.append(f"{msg['role'].capitalize()}: {msg['content']}")
        return "\n".join(parts)

    def _build_chat_messages(
        self,
        user_query: str,
        rag_context: str,
        history: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        """Build chat messages with RAG in a system message and clean user turns."""
        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history[:-1]
        ]
        if rag_context:
            messages.append({
                "role": "system",
                "content": (
                    "Use the following context when relevant:\n\n"
                    f"{rag_context}"
                ),
            })
        messages.append({"role": "user", "content": user_query})
        return messages

    def _prepare_llm_input(self, user_query: str) -> tuple[str, dict, list]:
        """
        Prepare prompt and kwargs for LLM generation including conversation history.

        Returns:
            Tuple of (prompt string, kwargs dict, retrieved chunks list)
        """
        memory_chunks = self.retriever.retrieve(user_query, top_k=self.retriever.top_k)

        kb_chunks: List[Dict] = []
        if self.kb_retriever.get_collection_count() > 0:
            kb_chunks = self.kb_retriever.retrieve(user_query, top_k=self.kb_retriever.top_k)

        self.last_query_retrieval = {
            "memory": len(memory_chunks),
            "kb": len(kb_chunks),
        }

        rag_context = self._format_rag_context(kb_chunks, memory_chunks)
        history = self.memory.get_conversation_messages()
        llm_type = self.llm.get_type()
        kwargs: dict = {}

        if llm_type in ("openai", "huggingface", "deepseek"):
            kwargs["messages"] = self._build_chat_messages(user_query, rag_context, history)
            prompt = user_query
        elif llm_type == "local":
            prompt = self._build_prompt(user_query, rag_context)
            prior_messages = history[:-1]
            history_text = self._format_history_as_text(prior_messages)
            if history_text:
                prompt = f"{history_text}\n\n{prompt}"
        else:
            prompt = self._build_prompt(user_query, rag_context)

        return prompt, kwargs, memory_chunks

    def _finalize_response(self, response: str) -> None:
        """Store assistant response and run post-processing."""
        self.memory.add_message("assistant", response)
        self.memory.store_conversation_chunk()

        if self.memory.should_summarize():
            logger.info("Summarization threshold reached, generating summary...")
            summary = self.memory.summarize_conversation()
            if summary:
                logger.info(f"Summary generated: {summary[:100]}...")

    def process_query(self, user_query: str) -> str:
        """
        Process a user query through the RAG pipeline.
        
        Args:
            user_query: User's input query
            
        Returns:
            Assistant's response
        """
        self.memory.add_message("user", user_query)
        prompt, llm_kwargs, retrieved_chunks = self._prepare_llm_input(user_query)

        start_time = time.time()
        try:
            response = self.llm.generate(prompt, **llm_kwargs)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            response = f"I apologize, but I encountered an error while generating a response: {str(e)}"
        latency_ms = (time.time() - start_time) * 1000

        self._finalize_response(response)
        self.observer.log_query(
            query=user_query,
            response=response,
            retrieved_chunks=retrieved_chunks,
            latency_ms=latency_ms,
            llm_type=self.llm.get_type(),
            tokens_estimated=(len(user_query) + len(response)) // 4,
        )
        return response

    def process_query_stream(self, user_query: str) -> Iterator[str]:
        """
        Process a user query and stream the response token by token.

        Args:
            user_query: User's input query

        Yields:
            Response text chunks as they are generated
        """
        self.memory.add_message("user", user_query)
        prompt, llm_kwargs, retrieved_chunks = self._prepare_llm_input(user_query)
        response_parts: List[str] = []

        start_time = time.time()
        try:
            for token in self.llm.stream_generate(prompt, **llm_kwargs):
                response_parts.append(token)
                yield token
            response = "".join(response_parts)
        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            if response_parts:
                response = "".join(response_parts)
            else:
                response = f"I apologize, but I encountered an error while generating a response: {str(e)}"
                yield response
        latency_ms = (time.time() - start_time) * 1000

        self._finalize_response(response)
        self.observer.log_query(
            query=user_query,
            response=response,
            retrieved_chunks=retrieved_chunks,
            latency_ms=latency_ms,
            llm_type=self.llm.get_type(),
            tokens_estimated=(len(user_query) + len(response)) // 4,
        )
    
    def get_llm_type(self) -> str:
        """Get the current LLM type."""
        return self.llm.get_type()
    
    def get_conversation_history(self):
        """Get the current conversation history."""
        return self.memory.get_conversation_history()
    
    def clear_conversation(self) -> None:
        """Clear the current conversation history."""
        self.memory.clear_conversation_history()


def main():
    """Main entry point for testing the pipeline."""
    try:
        pipeline = ChatbotPipeline()
        
        print("Chatbot Pipeline initialized successfully!")
        print(f"LLM Type: {pipeline.get_llm_type()}")
        print("\nYou can now use the Streamlit app (app.py) to interact with the chatbot.")
        print("Or test the pipeline directly here.")
        
        # Example usage
        # response = pipeline.process_query("Hello, how are you?")
        # print(f"\nResponse: {response}")
    
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        raise


if __name__ == "__main__":
    main()


