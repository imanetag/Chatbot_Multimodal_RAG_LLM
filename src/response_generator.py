"""
Response generation pipeline for the multimodal RAG chatbot
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
from src.retrieval_pipeline import get_retrieval_pipeline
from src.llm_manager import get_llm_manager
from src.prompt_manager import get_prompt_manager

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Class for generating responses using the RAG pipeline"""
    
    def __init__(self):
        """Initialize response generator"""
        self.db_manager = get_db_manager()
        self.retrieval_pipeline = get_retrieval_pipeline()
        self.llm_manager = get_llm_manager()
        self.prompt_manager = get_prompt_manager()
    
    def generate_response(self, query: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response to a user query
        
        Args:
            query: User query
            image_path: Path to image file (optional)
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Step 1: Detect use case
            use_case = self.prompt_manager.detect_use_case(query)
            
            # Step 2: Retrieve relevant information
            retrieval_result = self.retrieval_pipeline.retrieve(query, image_path=image_path)
            
            # Step 3: Build prompt with appropriate template
            context = retrieval_result.get("context", "")
            history = self.retrieval_pipeline.context_manager.get_conversation_history()
            
            image_description = ""
            if image_path:
                # In a full implementation, we would generate a description of the image
                # For now, we'll use a placeholder
                image_description = "Image fournie par l'utilisateur."
                use_case = "multimodal"  # Switch to multimodal template
            
            prompt = self.prompt_manager.get_prompt(
                use_case, context, query, history, image_description
            )
            
            # Step 4: Generate response using LLM
            if image_path:
                response_result = self.llm_manager.generate_response(query, image_path)
            else:
                response_result = self.llm_manager.generate_response(query)
            
            # Step 5: Add metadata and return
            response_result.update({
                "use_case": use_case,
                "prompt_template": use_case,
                "has_image": image_path is not None
            })
            
            return response_result
            
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
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.retrieval_pipeline.reset_conversation()
        self.llm_manager.reset_conversation()


# Singleton instance
_response_generator = None

def get_response_generator() -> ResponseGenerator:
    """Get or create the response generator singleton"""
    global _response_generator
    if _response_generator is None:
        _response_generator = ResponseGenerator()
    return _response_generator
