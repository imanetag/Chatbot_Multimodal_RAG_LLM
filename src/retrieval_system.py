"""
Retrieval system for the multimodal RAG chatbot
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from utils.db_manager import get_db_manager
from src.embedding_generator import get_embedding_generator

logger = logging.getLogger(__name__)

class RetrievalSystem:
    """Class for retrieving relevant information based on queries"""
    
    def __init__(self):
        """Initialize retrieval system"""
        self.db_manager = get_db_manager()
        self.embedding_generator = get_embedding_generator()
    
    def search(self, query: str, top_k: int = config.MAX_RESULTS, 
              threshold: float = config.VECTOR_SIMILARITY_THRESHOLD) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks based on a query
        
        Args:
            query: Search query
            top_k: Maximum number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_generator.generate_text_embedding(query)
            
            # Get all embeddings from the database
            all_embeddings = list(self.db_manager.embeddings.find())
            
            if not all_embeddings:
                logger.warning("No embeddings found in the database")
                return []
            
            # Calculate similarity scores
            results = []
            for embedding_doc in all_embeddings:
                vector = embedding_doc.get("vector")
                if not vector or len(vector) == 0:
                    continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, vector)
                
                if similarity >= threshold:
                    # Get the corresponding chunk
                    chunk_id = embedding_doc.get("chunk_id")
                    chunk = self.db_manager.chunks.find_one({"_id": chunk_id})
                    
                    if chunk:
                        # Get document metadata
                        document_id = chunk.get("document_id")
                        document = self.db_manager.get_document_by_id(document_id)
                        
                        results.append({
                            "chunk_id": chunk_id,
                            "document_id": document_id,
                            "text": chunk.get("text", ""),
                            "similarity": similarity,
                            "document_filename": document.get("filename") if document else None,
                            "document_type": document.get("file_type") if document else None
                        })
            
            # Sort by similarity (descending)
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Return top-k results
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error searching for query: {str(e)}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity (0-1)
        """
        try:
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0
    
    def search_multimodal(self, query: str, image_path: Optional[str] = None,
                         top_k: int = config.MAX_RESULTS,
                         threshold: float = config.VECTOR_SIMILARITY_THRESHOLD) -> List[Dict[str, Any]]:
        """
        Search for relevant information using both text and image
        
        Args:
            query: Text query
            image_path: Path to image file (optional)
            top_k: Maximum number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of relevant chunks with metadata
        """
        # For now, we'll just use text search since we have resource constraints
        # In a production environment, we would combine text and image embeddings
        return self.search(query, top_k, threshold)
    
    def build_context(self, query: str, top_k: int = config.MAX_RESULTS) -> str:
        """
        Build context for LLM based on a query
        
        Args:
            query: Search query
            top_k: Maximum number of chunks to include
            
        Returns:
            Context string for LLM
        """
        try:
            # Search for relevant chunks
            results = self.search(query, top_k)
            
            if not results:
                return "Aucune information pertinente trouvée dans la base de connaissances."
            
            # Build context
            context = "Contexte basé sur la base de connaissances :\n\n"
            
            for i, result in enumerate(results):
                context += f"[Document: {result['document_filename']}]\n"
                context += f"{result['text']}\n\n"
            
            return context
            
        except Exception as e:
            logger.error(f"Error building context: {str(e)}")
            return "Erreur lors de la construction du contexte."


# Singleton instance
_retrieval_system = None

def get_retrieval_system() -> RetrievalSystem:
    """Get or create the retrieval system singleton"""
    global _retrieval_system
    if _retrieval_system is None:
        _retrieval_system = RetrievalSystem()
    return _retrieval_system
