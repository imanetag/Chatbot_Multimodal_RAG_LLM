"""
Multimodal context fusion for the RAG chatbot
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
from src.retrieval_pipeline import get_retrieval_pipeline

logger = logging.getLogger(__name__)

class MultimodalFusion:
    """Class for fusing multimodal information with text context"""
    
    def __init__(self):
        """Initialize multimodal fusion"""
        self.db_manager = get_db_manager()
        self.multimodal_processor = get_multimodal_processor()
        self.retrieval_pipeline = get_retrieval_pipeline()
    
    def fuse_context(self, query: str, text_context: str, 
                    multimodal_file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Fuse text context with multimodal information
        
        Args:
            query: Original user query
            text_context: Retrieved text context
            multimodal_file_path: Path to multimodal file (optional)
            
        Returns:
            Fused context information
        """
        result = {
            "original_query": query,
            "text_context": text_context,
            "has_multimodal": False,
            "fused_context": text_context,
            "timestamp": datetime.now().isoformat()
        }
        
        if not multimodal_file_path:
            return result
        
        try:
            # Process the multimodal file
            multimodal_analysis = self.multimodal_processor.process_file(multimodal_file_path)
            
            # Determine file type
            file_extension = os.path.splitext(multimodal_file_path)[1].lower()
            
            if file_extension in config.SUPPORTED_IMAGE_TYPES:
                # Fuse image information with text context
                result["has_multimodal"] = True
                result["multimodal_type"] = "image"
                result["image_analysis"] = multimodal_analysis
                
                # Create fused context
                image_description = multimodal_analysis.get("description", "")
                image_text = multimodal_analysis.get("text", "")
                
                fused_context = "Contexte multimodal :\n\n"
                fused_context += f"[Description de l'image] {image_description}\n\n"
                
                if image_text:
                    fused_context += f"[Texte extrait de l'image] {image_text}\n\n"
                
                fused_context += "Contexte textuel :\n\n" + text_context
                
                result["fused_context"] = fused_context
                
            elif file_extension in config.SUPPORTED_AUDIO_TYPES:
                # Fuse audio information with text context
                result["has_multimodal"] = True
                result["multimodal_type"] = "audio"
                result["audio_analysis"] = multimodal_analysis
                
                # Create fused context
                audio_description = multimodal_analysis.get("description", "")
                transcription = multimodal_analysis.get("transcription", "")
                
                fused_context = "Contexte multimodal :\n\n"
                fused_context += f"[Description de l'audio] {audio_description}\n\n"
                
                if transcription and transcription != "Transcription non disponible en raison de contraintes de ressources.":
                    fused_context += f"[Transcription audio] {transcription}\n\n"
                
                fused_context += "Contexte textuel :\n\n" + text_context
                
                result["fused_context"] = fused_context
                
            elif file_extension in config.SUPPORTED_VIDEO_TYPES:
                # Fuse video information with text context
                result["has_multimodal"] = True
                result["multimodal_type"] = "video"
                result["video_analysis"] = multimodal_analysis
                
                # Create fused context
                video_description = multimodal_analysis.get("description", "")
                
                fused_context = "Contexte multimodal :\n\n"
                fused_context += f"[Description de la vidéo] {video_description}\n\n"
                
                # Add thumbnail information if available
                thumbnail = multimodal_analysis.get("thumbnail", {})
                thumbnail_text = thumbnail.get("text", "")
                thumbnail_description = thumbnail.get("description", "")
                
                if thumbnail_description:
                    fused_context += f"[Description de l'image extraite] {thumbnail_description}\n\n"
                
                if thumbnail_text:
                    fused_context += f"[Texte extrait de l'image] {thumbnail_text}\n\n"
                
                fused_context += "Contexte textuel :\n\n" + text_context
                
                result["fused_context"] = fused_context
            
            return result
            
        except Exception as e:
            logger.error(f"Error fusing context with multimodal: {str(e)}")
            result["error"] = str(e)
            return result


# Singleton instance
_multimodal_fusion = None

def get_multimodal_fusion() -> MultimodalFusion:
    """Get or create the multimodal fusion singleton"""
    global _multimodal_fusion
    if _multimodal_fusion is None:
        _multimodal_fusion = MultimodalFusion()
    return _multimodal_fusion
