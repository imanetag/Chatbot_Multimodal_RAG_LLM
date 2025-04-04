"""
Context window management for the multimodal RAG chatbot
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

logger = logging.getLogger(__name__)

class ContextManager:
    """Class for managing context window for LLM"""
    
    def __init__(self, max_context_length: int = 4000):
        """
        Initialize context manager
        
        Args:
            max_context_length: Maximum length of context in tokens/characters
        """
        self.max_context_length = max_context_length
        self.retrieval_system = get_retrieval_system()
        self.db_manager = get_db_manager()
        self.conversation_history = []
    
    def add_message(self, role: str, content: str):
        """
        Add a message to the conversation history
        
        Args:
            role: Message role (user or assistant)
            content: Message content
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim history if it gets too long
        self._trim_history()
    
    def _trim_history(self):
        """Trim conversation history to fit within context window"""
        total_length = sum(len(msg["content"]) for msg in self.conversation_history)
        
        while total_length > self.max_context_length and len(self.conversation_history) > 2:
            # Remove oldest messages, but keep at least the last exchange
            removed_msg = self.conversation_history.pop(0)
            total_length -= len(removed_msg["content"])
    
    def get_conversation_history(self) -> str:
        """
        Get formatted conversation history
        
        Returns:
            Formatted conversation history
        """
        history = ""
        for msg in self.conversation_history:
            role_prefix = "Utilisateur: " if msg["role"] == "user" else "Assistant: "
            history += f"{role_prefix}{msg['content']}\n\n"
        
        return history
    
    def build_prompt(self, query: str, include_history: bool = True, 
                    include_retrieved_context: bool = True) -> str:
        """
        Build a prompt for the LLM
        
        Args:
            query: User query
            include_history: Whether to include conversation history
            include_retrieved_context: Whether to include retrieved context
            
        Returns:
            Complete prompt for LLM
        """
        prompt_parts = []
        
        # System instructions
        system_prompt = """Tu es un assistant d'entreprise multimodal basé sur RAG (Retrieval-Augmented Generation).
Tu réponds aux questions en te basant sur le contexte fourni à partir de la base de connaissances de l'entreprise.
Si tu ne trouves pas l'information dans le contexte fourni, indique-le clairement.
Réponds toujours en français de manière professionnelle et concise."""
        
        prompt_parts.append(system_prompt)
        
        # Add conversation history if requested
        if include_history and self.conversation_history:
            prompt_parts.append("\nHistorique de la conversation:\n" + self.get_conversation_history())
        
        # Add retrieved context if requested
        if include_retrieved_context:
            retrieved_context = self.retrieval_system.build_context(query)
            prompt_parts.append("\nContexte récupéré:\n" + retrieved_context)
        
        # Add current query
        prompt_parts.append("\nQuestion actuelle: " + query)
        prompt_parts.append("\nRéponse:")
        
        return "\n".join(prompt_parts)
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []


# Singleton instance
_context_manager = None

def get_context_manager() -> ContextManager:
    """Get or create the context manager singleton"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
