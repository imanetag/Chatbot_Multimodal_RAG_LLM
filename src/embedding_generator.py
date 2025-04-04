"""
Embedding generation module for the multimodal RAG chatbot
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

class EmbeddingGenerator:
    """Base class for generating embeddings"""
    
    def __init__(self):
        """Initialize embedding generator"""
        self.db_manager = get_db_manager()
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize embedding models"""
        try:
            # For text embeddings, use a lightweight model due to memory constraints
            # We'll use a simple TF-IDF vectorizer as a fallback
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.text_vectorizer = TfidfVectorizer(
                max_features=768,  # Typical embedding dimension
                stop_words=['en', 'fr']  # English and French stopwords
            )
            self.text_vectorizer_fitted = False
            
            logger.info("Initialized TF-IDF vectorizer for text embeddings")
            
            # Note: In a production environment with more resources, we would use:
            # from sentence_transformers import SentenceTransformer
            # self.text_model = SentenceTransformer(config.TEXT_EMBEDDING_MODEL)
            
            # For image embeddings, we'll use a placeholder for now
            # In production, we would use CLIP or similar models
            logger.info("Using placeholder for image embeddings due to resource constraints")
            
        except Exception as e:
            logger.error(f"Error initializing embedding models: {str(e)}")
            raise
    
    def generate_text_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            if not text or len(text.strip()) == 0:
                # Return zero vector for empty text
                return [0.0] * 768
            
            # Using TF-IDF as a lightweight alternative
            if not self.text_vectorizer_fitted:
                # Fit on first use
                self.text_vectorizer.fit([text])
                self.text_vectorizer_fitted = True
            
            vector = self.text_vectorizer.transform([text]).toarray()[0]
            
            # Normalize the vector
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            return vector.tolist()
            
            # In production with more resources:
            # return self.text_model.encode(text).tolist()
            
        except Exception as e:
            logger.error(f"Error generating text embedding: {str(e)}")
            # Return zero vector on error
            return [0.0] * 768
    
    def generate_image_embedding(self, image_path: str) -> List[float]:
        """
        Generate embedding for image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Embedding vector
        """
        try:
            # Placeholder: In production, we would use CLIP or similar models
            # For now, return a random vector as a placeholder
            import numpy as np
            np.random.seed(hash(image_path) % 2**32)
            vector = np.random.randn(512)
            vector = vector / np.linalg.norm(vector)
            
            return vector.tolist()
            
        except Exception as e:
            logger.error(f"Error generating image embedding: {str(e)}")
            # Return zero vector on error
            return [0.0] * 512
    
    def process_document_embeddings(self, document_id: str) -> List[str]:
        """
        Process all chunks of a document and generate embeddings
        
        Args:
            document_id: Document ID
            
        Returns:
            List of embedding IDs
        """
        try:
            # Get all chunks for the document
            chunks = self.db_manager.get_chunks_by_document_id(document_id)
            
            if not chunks:
                logger.warning(f"No chunks found for document {document_id}")
                return []
            
            # Generate embeddings for each chunk
            embeddings_data = []
            for chunk in chunks:
                embedding_vector = self.generate_text_embedding(chunk["text"])
                
                embeddings_data.append({
                    "document_id": document_id,
                    "chunk_id": str(chunk["_id"]),
                    "vector": embedding_vector,
                    "vector_dimension": len(embedding_vector),
                    "created_at": datetime.now()
                })
            
            # Store embeddings
            if embeddings_data:
                embedding_ids = self.db_manager.store_embeddings(embeddings_data)
                logger.info(f"Generated {len(embedding_ids)} embeddings for document {document_id}")
                return embedding_ids
            
            return []
            
        except Exception as e:
            logger.error(f"Error processing document embeddings for {document_id}: {str(e)}")
            return []


# Singleton instance
_embedding_generator = None

def get_embedding_generator() -> EmbeddingGenerator:
    """Get or create the embedding generator singleton"""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator
