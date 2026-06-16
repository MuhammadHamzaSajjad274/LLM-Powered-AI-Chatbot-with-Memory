"""
Memory class for managing long-term chat memory with ChromaDB persistence, RAG context, and summarization.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from .retriever import Retriever
from .llm import LLMModel

logger = logging.getLogger(__name__)


class Memory:
    """
    Class for managing long-term chat memory with RAG and summarization.
    """
    
    def __init__(
        self,
        retriever: Retriever,
        llm: LLMModel,
        summarization_threshold: int = 20
    ):
        """
        Initialize the Memory manager.
        
        Args:
            retriever: Retriever instance for vector search
            llm: LLM instance for generating summaries
            summarization_threshold: Number of user-assistant turns before summarization
        """
        self.retriever = retriever
        self.llm = llm
        self.summarization_threshold = summarization_threshold
        self.message_count = 0
        self.conversation_history: List[Dict[str, str]] = []
        logger.info(f"Memory initialized with summarization threshold: {summarization_threshold}")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: Message role ("user" or "assistant")
            content: Message content
            metadata: Optional metadata dictionary
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        self.message_count += 1
        
        logger.debug(f"Added {role} message. Total messages: {self.message_count}")
    
    def get_rag_context(self, query: str) -> str:
        """
        Retrieve relevant context from memory for RAG.
        
        Args:
            query: User query to find relevant context for
            
        Returns:
            Formatted context string to prepend to the query
        """
        # Retrieve top-k relevant chunks
        retrieved_docs = self.retriever.retrieve(query, top_k=self.retriever.top_k)
        
        if not retrieved_docs:
            return ""
        
        # Format context from retrieved documents
        context_parts = []
        for doc in retrieved_docs:
            context_parts.append(f"Previous conversation: {doc['text']}")
        
        context = "\n\n".join(context_parts)
        logger.debug(f"Retrieved {len(retrieved_docs)} context chunks for RAG")
        
        return context
    
    def should_summarize(self) -> bool:
        """
        Check if conversation should be summarized based on message count.
        
        Returns:
            True if summarization threshold is reached
        """
        # Count user-assistant pairs (turns)
        user_messages = sum(1 for msg in self.conversation_history if msg["role"] == "user")
        return user_messages >= self.summarization_threshold
    
    def summarize_conversation(self) -> Optional[str]:
        """
        Generate a summary of the current conversation chunk and store it.
        
        Returns:
            Generated summary string or None if summarization fails
        """
        if not self.conversation_history:
            return None
        
        # Format conversation for summarization
        conversation_text = self._format_conversation_for_summary()
        
        # Generate summary using LLM
        summary_prompt = f"""Please provide a concise summary of the following conversation. 
Focus on key topics, decisions, and important information that should be remembered for future interactions.

Conversation:
{conversation_text}

Summary:"""
        
        try:
            summary = self.llm.generate(summary_prompt)
            logger.info("Generated conversation summary")
            
            # Store summary in ChromaDB
            summary_id = f"summary_{uuid.uuid4().hex[:8]}"
            self.retriever.add_documents(
                texts=[summary],
                metadatas=[{
                    "type": "summary",
                    "timestamp": datetime.now().isoformat(),
                    "message_count": self.message_count
                }],
                ids=[summary_id]
            )
            
            # Clear the conversation history chunk (keep last few messages for context)
            # Keep the last 2 messages to maintain some immediate context
            messages_to_keep = min(2, len(self.conversation_history))
            self.conversation_history = self.conversation_history[-messages_to_keep:]
            
            # Reset message count (but keep track of total)
            self.message_count = len(self.conversation_history)
            
            logger.info(f"Stored summary and cleared conversation history (kept {messages_to_keep} recent messages)")
            return summary
        
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
    
    def _format_conversation_for_summary(self) -> str:
        """
        Format conversation history as text for summarization.
        
        Returns:
            Formatted conversation string
        """
        formatted_parts = []
        for msg in self.conversation_history:
            role = msg["role"].capitalize()
            content = msg["content"]
            formatted_parts.append(f"{role}: {content}")
        
        return "\n".join(formatted_parts)
    
    def store_conversation_chunk(self) -> None:
        """
        Store the current conversation chunk in ChromaDB.
        This is called after a complete user-assistant exchange.
        """
        if not self.conversation_history:
            return
        
        # Store only the most recent user + assistant exchange
        recent_messages = self.conversation_history[-2:]
        formatted_parts = []
        for msg in recent_messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            formatted_parts.append(f"{role}: {content}")
        conversation_text = "\n".join(formatted_parts)
        
        # Generate a unique ID for this chunk
        chunk_id = f"chunk_{uuid.uuid4().hex[:8]}"
        
        # Store in ChromaDB
        self.retriever.add_documents(
            texts=[conversation_text],
            metadatas=[{
                "type": "conversation_chunk",
                "timestamp": datetime.now().isoformat(),
                "message_count": self.message_count
            }],
            ids=[chunk_id]
        )
        
        logger.debug(f"Stored conversation chunk: {chunk_id}")
    
    def get_conversation_messages(self) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for LLM backends.
        
        Returns:
            List of message dicts with role and content keys
        """
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversation_history
        ]
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            List of message dictionaries
        """
        return self.conversation_history.copy()
    
    def clear_conversation_history(self) -> None:
        """Clear the current conversation history."""
        self.conversation_history = []
        self.message_count = 0
        logger.info("Cleared conversation history")


