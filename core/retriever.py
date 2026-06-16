"""
Retriever class for performing Top-K search on ChromaDB.
"""

import logging
from typing import List, Dict, Any, Optional
import chromadb

logger = logging.getLogger(__name__)


class Retriever:
    """
    Class for performing vector search on ChromaDB to retrieve relevant context.
    """
    
    def __init__(
        self,
        collection_name: str,
        persist_directory: str,
        embedder,
        top_k: int = 3
    ):
        """
        Initialize the Retriever.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory path for ChromaDB persistence
            embedder: Embedder instance for generating query embeddings
            top_k: Number of top results to retrieve
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedder = embedder
        self.top_k = top_k
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        logger.info(f"Retriever initialized with top_k={top_k}")
    
    def _get_or_create_collection(self):
        """Get existing collection or create a new one."""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Retrieved existing collection: {self.collection_name}")
        except Exception:
            # Collection doesn't exist, create it
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
        
        return collection
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve top-k most relevant documents for a query.
        
        Args:
            query: Query text to search for
            top_k: Number of results to retrieve (defaults to self.top_k)
            
        Returns:
            List of dictionaries containing retrieved documents with metadata
        """
        if top_k is None:
            top_k = self.top_k
        
        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)
        
        # Query ChromaDB
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self.collection.count()),
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results, filtering by cosine distance threshold
            retrieved_docs = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    distance = results["distances"][0][i] if results["distances"] else None
                    if distance is not None and distance >= 0.4:
                        continue
                    doc = {
                        "id": results["ids"][0][i],
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": distance
                    }
                    retrieved_docs.append(doc)
            
            logger.debug(f"Retrieved {len(retrieved_docs)} documents for query")
            return retrieved_docs
        
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the collection.
        
        Args:
            texts: List of document texts
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
        """
        if not texts:
            return
        
        # Generate embeddings
        embeddings = self.embedder.embed_documents(texts)
        
        # Prepare metadata and IDs
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        if ids is None:
            # Generate IDs based on collection count
            current_count = self.collection.count()
            ids = [f"doc_{current_count + i}" for i in range(len(texts))]
        
        # Add to collection
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(texts)} documents to collection")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        return self.collection.count()


