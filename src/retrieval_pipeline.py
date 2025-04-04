"""
Retrieval pipeline for the multimodal RAG chatbot
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from utils.db_manager import get_db_manager
from src.retrieval_system import get_retrieval_system
from src.context_manager import get_context_manager
from src.relevance_scorer import get_relevance_scorer

logger = logging.getLogger(__name__)

class RetrievalPipeline:
    """Main class for the retrieval pipeline"""
    
    def __init__(self):
        """Initialize retrieval pipeline"""
        self.db_manager = get_db_manager()
        self.retrieval_system = get_retrieval_system()
        self.context_manager = get_context_manager()
        self.relevance_scorer = get_relevance_scorer()
    
    def retrieve(self, query: str, top_k: int = config.MAX_RESULTS,
                image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve relevant information based on a query
        
        Args:
            query: User query
            top_k: Maximum number of results to return
            image_path: Path to image file (optional)
            
        Returns:
            Dictionary with retrieval results
        """
        try:
            # Step 1: Search for relevant chunks
            if image_path:
                # Multimodal search
                search_results = self.retrieval_system.search_multimodal(
                    query, image_path, top_k
                )
            else:
                # Text-only search
                search_results = self.retrieval_system.search(query, top_k)
            
            # Step 2: Rerank results
            reranked_results = self.relevance_scorer.rerank_results(query, search_results)
            
            # Step 3: Build context for LLM
            context = self._build_context_from_results(query, reranked_results)
            
            # Step 4: Build complete prompt
            prompt = self.context_manager.build_prompt(
                query, 
                include_history=True,
                include_retrieved_context=False  # We'll use our custom context
            )
            
            # Return results
            return {
                "query": query,
                "results": reranked_results,
                "context": context,
                "prompt": prompt,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in retrieval pipeline: {str(e)}")
            return {
                "query": query,
                "error": str(e),
                "results": [],
                "context": "Erreur lors de la récupération des informations.",
                "prompt": self.context_manager.build_prompt(
                    query, include_retrieved_context=False
                ),
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_context_from_results(self, query: str, results: List[Dict[str, Any]]) -> str:
        """
        Build context from search results
        
        Args:
            query: Original query
            results: Search results
            
        Returns:
            Formatted context
        """
        if not results:
            return "Aucune information pertinente trouvée dans la base de connaissances."
        
        context = "Contexte basé sur la base de connaissances :\n\n"
        
        # Group results by document
        documents = {}
        for result in results:
            doc_id = result["document_id"]
            if doc_id not in documents:
                documents[doc_id] = {
                    "filename": result["document_filename"],
                    "type": result["document_type"],
                    "chunks": []
                }
            documents[doc_id]["chunks"].append(result)
        
        # Add document sections to context
        for doc_id, doc_info in documents.items():
            context += f"[Document: {doc_info['filename']}]\n"
            
            # Sort chunks by their position in the document
            doc_info["chunks"].sort(key=lambda x: x.get("chunk_index", 0))
            
            # Add chunk text
            for chunk in doc_info["chunks"]:
                context += f"{chunk['text']}\n\n"
        
        return context
    
    def add_user_message(self, message: str):
        """
        Add a user message to the conversation history
        
        Args:
            message: User message
        """
        self.context_manager.add_message("user", message)
    
    def add_assistant_message(self, message: str):
        """
        Add an assistant message to the conversation history
        
        Args:
            message: Assistant message
        """
        self.context_manager.add_message("assistant", message)
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.context_manager.reset_conversation()


# Singleton instance
_retrieval_pipeline = None

def get_retrieval_pipeline() -> RetrievalPipeline:
    """Get or create the retrieval pipeline singleton"""
    global _retrieval_pipeline
    if _retrieval_pipeline is None:
        _retrieval_pipeline = RetrievalPipeline()
    return _retrieval_pipeline
