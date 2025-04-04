"""
LLM integration module for the multimodal RAG chatbot
"""

import os
import sys
import logging
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from utils.db_manager import get_db_manager
from src.retrieval_pipeline import get_retrieval_pipeline

logger = logging.getLogger(__name__)

class LLMManager:
    """Class for managing LLM integration"""
    
    def __init__(self):
        """Initialize LLM manager"""
        self.db_manager = get_db_manager()
        self.retrieval_pipeline = get_retrieval_pipeline()
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM based on configuration"""
        try:
            # Check if model directory exists
            os.makedirs(config.LLM_MODEL_PATH, exist_ok=True)
            
            # For now, we'll use a lightweight approach due to memory constraints
            # In production, we would download and use Gemma or DeepSeek Janus
            logger.info("Using lightweight LLM approach due to resource constraints")
            
            # Set model type flag
            self.model_initialized = False
            self.model_type = config.LLM_MODEL_TYPE
            
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            self.model_initialized = False
    
    def generate_response(self, query: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response using the LLM
        
        Args:
            query: User query
            image_path: Path to image file (optional)
            
        Returns:
            Dictionary with generation results
        """
        try:
            # Step 1: Retrieve relevant information
            retrieval_result = self.retrieval_pipeline.retrieve(query, image_path=image_path)
            
            # Step 2: Generate response
            if self.model_initialized:
                # Use the actual LLM if initialized
                response_text = self._generate_with_llm(retrieval_result["prompt"])
            else:
                # Use a fallback approach
                response_text = self._generate_fallback(query, retrieval_result)
            
            # Step 3: Add to conversation history
            self.retrieval_pipeline.add_user_message(query)
            self.retrieval_pipeline.add_assistant_message(response_text)
            
            # Return results
            return {
                "query": query,
                "response": response_text,
                "context_used": retrieval_result.get("context", ""),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            error_response = f"Désolé, je n'ai pas pu générer une réponse en raison d'une erreur: {str(e)}"
            
            # Add to conversation history
            self.retrieval_pipeline.add_user_message(query)
            self.retrieval_pipeline.add_assistant_message(error_response)
            
            return {
                "query": query,
                "response": error_response,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_with_llm(self, prompt: str) -> str:
        """
        Generate response using the LLM
        
        Args:
            prompt: Complete prompt for the LLM
            
        Returns:
            Generated response
        """
        # This would be implemented with the actual LLM API
        # For now, we'll use a fallback approach
        return "Cette fonctionnalité sera implémentée avec le modèle complet."
    
    def _generate_fallback(self, query: str, retrieval_result: Dict[str, Any]) -> str:
        """
        Generate a fallback response based on retrieved information
        
        Args:
            query: User query
            retrieval_result: Retrieval results
            
        Returns:
            Generated response
        """
        results = retrieval_result.get("results", [])
        
        if not results:
            return "Je n'ai pas trouvé d'informations pertinentes dans la base de connaissances pour répondre à votre question. Pourriez-vous reformuler ou poser une question différente ?"
        
        # Build a response based on the retrieved chunks
        response = "Voici les informations que j'ai trouvées dans la base de connaissances :\n\n"
        
        # Group by document
        documents = {}
        for result in results[:3]:  # Use top 3 results
            doc_id = result["document_id"]
            if doc_id not in documents:
                documents[doc_id] = {
                    "filename": result["document_filename"],
                    "chunks": []
                }
            documents[doc_id]["chunks"].append(result)
        
        # Add information from each document
        for doc_id, doc_info in documents.items():
            response += f"Dans le document '{doc_info['filename']}':\n"
            
            for chunk in doc_info["chunks"]:
                # Extract a relevant snippet (first 200 characters)
                snippet = chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"]
                response += f"- {snippet}\n\n"
        
        response += "Ces informations répondent-elles à votre question ? Si vous avez besoin de plus de détails, n'hésitez pas à me le faire savoir."
        
        return response
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.retrieval_pipeline.reset_conversation()


# Singleton instance
_llm_manager = None

def get_llm_manager() -> LLMManager:
    """Get or create the LLM manager singleton"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager
