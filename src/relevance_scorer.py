"""
Relevance scoring and reranking module for the multimodal RAG chatbot
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

logger = logging.getLogger(__name__)

class RelevanceScorer:
    """Class for scoring and reranking search results"""
    
    def __init__(self):
        """Initialize relevance scorer"""
        self.db_manager = get_db_manager()
    
    def rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rerank search results based on additional relevance factors
        
        Args:
            query: Original search query
            results: Initial search results based on vector similarity
            
        Returns:
            Reranked results
        """
        try:
            if not results:
                return []
            
            # Apply additional scoring factors
            for result in results:
                # Start with the original similarity score
                base_score = result["similarity"]
                
                # Apply text matching boost
                text_match_score = self._calculate_text_match_score(query, result["text"])
                
                # Apply recency boost if available
                recency_score = self._calculate_recency_score(result["document_id"])
                
                # Calculate final score
                final_score = (
                    base_score * 0.7 +  # Vector similarity (70% weight)
                    text_match_score * 0.2 +  # Text matching (20% weight)
                    recency_score * 0.1  # Recency (10% weight)
                )
                
                # Update the result with the new score
                result["original_similarity"] = result["similarity"]
                result["text_match_score"] = text_match_score
                result["recency_score"] = recency_score
                result["final_score"] = final_score
            
            # Sort by final score (descending)
            results.sort(key=lambda x: x["final_score"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error reranking results: {str(e)}")
            return results  # Return original results on error
    
    def _calculate_text_match_score(self, query: str, text: str) -> float:
        """
        Calculate text matching score based on keyword presence
        
        Args:
            query: Search query
            text: Chunk text
            
        Returns:
            Text matching score (0-1)
        """
        try:
            # Simple keyword matching
            query_words = set(query.lower().split())
            text_lower = text.lower()
            
            # Count matching words
            matches = sum(1 for word in query_words if word in text_lower)
            
            # Calculate score
            if len(query_words) == 0:
                return 0.0
            
            return matches / len(query_words)
            
        except Exception as e:
            logger.error(f"Error calculating text match score: {str(e)}")
            return 0.0
    
    def _calculate_recency_score(self, document_id: str) -> float:
        """
        Calculate recency score based on document creation time
        
        Args:
            document_id: Document ID
            
        Returns:
            Recency score (0-1)
        """
        try:
            # Get document metadata
            document = self.db_manager.get_document_by_id(document_id)
            
            if not document or "created_at" not in document:
                return 0.5  # Default score if no timestamp
            
            # Calculate days since creation
            created_at = document["created_at"]
            now = datetime.now()
            
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except ValueError:
                    return 0.5
            
            days_old = (now - created_at).days
            
            # Newer documents get higher scores
            # 0 days old = 1.0, 30 days old = 0.5, 60+ days old = 0.0
            if days_old <= 0:
                return 1.0
            elif days_old >= 60:
                return 0.0
            else:
                return 1.0 - (days_old / 60)
            
        except Exception as e:
            logger.error(f"Error calculating recency score: {str(e)}")
            return 0.5  # Default score on error


# Singleton instance
_relevance_scorer = None

def get_relevance_scorer() -> RelevanceScorer:
    """Get or create the relevance scorer singleton"""
    global _relevance_scorer
    if _relevance_scorer is None:
        _relevance_scorer = RelevanceScorer()
    return _relevance_scorer
