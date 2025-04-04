"""
Prompt engineering module for the multimodal RAG chatbot
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

logger = logging.getLogger(__name__)

class PromptManager:
    """Class for managing prompts for the LLM"""
    
    def __init__(self):
        """Initialize prompt manager"""
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """
        Load prompt templates
        
        Returns:
            Dictionary of prompt templates
        """
        return {
            "default": """Tu es un assistant d'entreprise multimodal basé sur RAG (Retrieval-Augmented Generation).
Tu réponds aux questions en te basant sur le contexte fourni à partir de la base de connaissances de l'entreprise.
Si tu ne trouves pas l'information dans le contexte fourni, indique-le clairement.
Réponds toujours en français de manière professionnelle et concise.

{context}

Historique de la conversation:
{history}

Question: {query}
Réponse:""",

            "employee_assistance": """Tu es un assistant d'entreprise spécialisé dans l'aide aux employés.
Tu réponds aux questions concernant les ressources humaines, l'informatique, la logistique et l'onboarding.
Base tes réponses uniquement sur le contexte fourni à partir de la base de connaissances de l'entreprise.
Si tu ne trouves pas l'information dans le contexte fourni, indique-le clairement.
Réponds toujours en français de manière professionnelle et concise.

{context}

Historique de la conversation:
{history}

Question: {query}
Réponse:""",

            "knowledge_management": """Tu es un assistant d'entreprise spécialisé dans la gestion des connaissances.
Tu aides à rechercher des informations dans la documentation de l'entreprise.
Base tes réponses uniquement sur le contexte fourni à partir de la base de connaissances de l'entreprise.
Si tu ne trouves pas l'information dans le contexte fourni, indique-le clairement.
Réponds toujours en français de manière professionnelle et concise.

{context}

Historique de la conversation:
{history}

Question: {query}
Réponse:""",

            "maintenance": """Tu es un assistant d'entreprise spécialisé dans la maintenance et le diagnostic.
Tu aides à identifier les pièces et à fournir des guides de dépannage.
Base tes réponses uniquement sur le contexte fourni à partir de la base de connaissances de l'entreprise.
Si tu ne trouves pas l'information dans le contexte fourni, indique-le clairement.
Réponds toujours en français de manière professionnelle et concise.

{context}

Historique de la conversation:
{history}

Question: {query}
Réponse:""",

            "helpdesk": """Tu es un assistant d'entreprise spécialisé dans le support informatique.
Tu aides à résoudre les problèmes informatiques courants et à répondre aux questions sur les logiciels.
Base tes réponses uniquement sur le contexte fourni à partir de la base de connaissances de l'entreprise.
Si tu ne trouves pas l'information dans le contexte fourni, indique-le clairement.
Réponds toujours en français de manière professionnelle et concise.

{context}

Historique de la conversation:
{history}

Question: {query}
Réponse:""",

            "multimodal": """Tu es un assistant d'entreprise multimodal capable de comprendre et d'analyser des images.
Tu réponds aux questions en te basant sur le contexte fourni et l'analyse de l'image.
Si tu ne trouves pas l'information dans le contexte fourni ou l'image, indique-le clairement.
Réponds toujours en français de manière professionnelle et concise.

{context}

Description de l'image: {image_description}

Historique de la conversation:
{history}

Question: {query}
Réponse:"""
        }
    
    def get_prompt(self, template_name: str, context: str, query: str, 
                  history: str = "", image_description: str = "") -> str:
        """
        Get a formatted prompt based on a template
        
        Args:
            template_name: Name of the template to use
            context: Retrieved context
            query: User query
            history: Conversation history
            image_description: Description of image (for multimodal)
            
        Returns:
            Formatted prompt
        """
        try:
            # Get template
            template = self.templates.get(template_name, self.templates["default"])
            
            # Format prompt
            prompt = template.format(
                context=context,
                query=query,
                history=history,
                image_description=image_description
            )
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error formatting prompt: {str(e)}")
            # Fallback to default template
            return self.templates["default"].format(
                context=context,
                query=query,
                history=history,
                image_description=""
            )
    
    def detect_use_case(self, query: str) -> str:
        """
        Detect the most appropriate use case for a query
        
        Args:
            query: User query
            
        Returns:
            Template name for the detected use case
        """
        query_lower = query.lower()
        
        # Simple keyword-based detection
        if any(word in query_lower for word in ["rh", "ressources humaines", "congé", "salaire", "contrat", 
                                               "onboarding", "formation", "nouveau employé"]):
            return "employee_assistance"
        
        elif any(word in query_lower for word in ["document", "documentation", "procédure", "manuel", 
                                                 "guide", "recherche", "trouver", "où est"]):
            return "knowledge_management"
        
        elif any(word in query_lower for word in ["panne", "réparer", "maintenance", "diagnostic", 
                                                 "pièce", "équipement", "machine", "outil"]):
            return "maintenance"
        
        elif any(word in query_lower for word in ["informatique", "ordinateur", "logiciel", "mot de passe", 
                                                 "compte", "accès", "problème", "bug", "erreur"]):
            return "helpdesk"
        
        # Default case
        return "default"


# Singleton instance
_prompt_manager = None

def get_prompt_manager() -> PromptManager:
    """Get or create the prompt manager singleton"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager
