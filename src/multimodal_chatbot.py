"""
Multimodal RAG chatbot integration module
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
from src.multimodal_processor import get_multimodal_processor
from src.multimodal_fusion import get_multimodal_fusion
from src.retrieval_pipeline import get_retrieval_pipeline
from src.response_generator import get_response_generator

logger = logging.getLogger(__name__)

class MultimodalChatbot:
    """Main class for the multimodal RAG chatbot"""
    
    def __init__(self):
        """Initialize multimodal chatbot"""
        self.db_manager = get_db_manager()
        self.multimodal_processor = get_multimodal_processor()
        self.multimodal_fusion = get_multimodal_fusion()
        self.retrieval_pipeline = get_retrieval_pipeline()
        self.response_generator = get_response_generator()
    
    def process_query(self, query: str, multimodal_file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query with optional multimodal input
        
        Args:
            query: User query
            multimodal_file_path: Path to multimodal file (optional)
            
        Returns:
            Response with metadata
        """
        try:
            # Step 1: Process multimodal input if provided
            multimodal_info = None
            if multimodal_file_path:
                multimodal_info = self.multimodal_processor.process_file(multimodal_file_path)
            
            # Step 2: Enhance query with multimodal information
            if multimodal_file_path:
                enhanced_query_info = self.multimodal_processor.enhance_query_with_multimodal(
                    query, multimodal_file_path
                )
                enhanced_query = enhanced_query_info.get("enhanced_query", query)
            else:
                enhanced_query = query
                enhanced_query_info = None
            
            # Step 3: Retrieve relevant information
            retrieval_result = self.retrieval_pipeline.retrieve(enhanced_query)
            
            # Step 4: Fuse text context with multimodal information
            if multimodal_file_path:
                fused_context_info = self.multimodal_fusion.fuse_context(
                    query, retrieval_result.get("context", ""), multimodal_file_path
                )
                fused_context = fused_context_info.get("fused_context", "")
            else:
                fused_context = retrieval_result.get("context", "")
                fused_context_info = None
            
            # Step 5: Generate response
            response_result = self.response_generator.generate_response(query, multimodal_file_path)
            
            # Step 6: Add metadata and return
            result = {
                "query": query,
                "response": response_result.get("response", ""),
                "has_multimodal": multimodal_file_path is not None,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add detailed information if available
            if multimodal_info:
                result["multimodal_info"] = multimodal_info
            
            if enhanced_query_info:
                result["enhanced_query_info"] = enhanced_query_info
            
            if fused_context_info:
                result["fused_context_info"] = fused_context_info
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            error_response = f"Désolé, je n'ai pas pu traiter votre demande en raison d'une erreur: {str(e)}"
            
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
        self.response_generator.reset_conversation()


# Singleton instance
_multimodal_chatbot = None

def get_multimodal_chatbot() -> MultimodalChatbot:
    """Get or create the multimodal chatbot singleton"""
    global _multimodal_chatbot
    if _multimodal_chatbot is None:
        _multimodal_chatbot = MultimodalChatbot()
    return _multimodal_chatbot
