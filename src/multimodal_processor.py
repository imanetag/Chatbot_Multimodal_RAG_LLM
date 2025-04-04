"""
Image understanding module for the multimodal RAG chatbot
"""

import os
import sys
import logging
import tempfile
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from PIL import Image

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from utils.db_manager import get_db_manager

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Enhanced class for processing and understanding images"""
    
    def __init__(self):
        """Initialize image processor"""
        self.db_manager = get_db_manager()
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize image processing models"""
        try:
            # For now, we'll use a lightweight approach due to memory constraints
            # In production, we would use CLIP, ViT, or similar models
            logger.info("Using lightweight image processing due to resource constraints")
            
            # Import necessary libraries for basic image processing
            import numpy as np
            from PIL import Image
            
            # Set model initialized flag
            self.model_initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing image processing models: {str(e)}")
            self.model_initialized = False
    
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process an image and extract information
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with image analysis results
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Open and validate image
            image = Image.open(image_path)
            
            # Extract basic image properties
            width, height = image.size
            format_type = image.format
            mode = image.mode
            
            # Extract EXIF data if available
            exif_data = {}
            if hasattr(image, '_getexif') and image._getexif() is not None:
                exif = image._getexif()
                if exif:
                    for tag, value in exif.items():
                        exif_data[tag] = str(value)
            
            # Generate a basic description
            description = self._generate_image_description(image, image_path)
            
            # Extract text from image using OCR (if available)
            text = self._extract_text_from_image(image)
            
            # Return results
            return {
                "filename": os.path.basename(image_path),
                "width": width,
                "height": height,
                "format": format_type,
                "mode": mode,
                "description": description,
                "text": text,
                "exif": exif_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            return {
                "filename": os.path.basename(image_path) if image_path else "unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_image_description(self, image: Image.Image, image_path: str) -> str:
        """
        Generate a description of the image
        
        Args:
            image: PIL Image object
            image_path: Path to the image file
            
        Returns:
            Image description
        """
        try:
            # In a production environment, we would use a vision model
            # For now, we'll use a simple approach based on image properties
            
            width, height = image.size
            aspect_ratio = width / height
            
            # Analyze colors
            try:
                # Get dominant colors
                colors = image.convert('RGB').getcolors(maxcolors=10000)
                if colors:
                    # Sort by count (descending)
                    colors.sort(key=lambda x: x[0], reverse=True)
                    dominant_color = colors[0][1]
                    
                    # Simple color naming
                    color_names = {
                        (0, 0, 0): "noir",
                        (255, 255, 255): "blanc",
                        (255, 0, 0): "rouge",
                        (0, 255, 0): "vert",
                        (0, 0, 255): "bleu",
                        (255, 255, 0): "jaune",
                        (255, 0, 255): "magenta",
                        (0, 255, 255): "cyan",
                        (128, 128, 128): "gris"
                    }
                    
                    # Find closest color
                    min_distance = float('inf')
                    color_name = "inconnu"
                    
                    for rgb, name in color_names.items():
                        distance = sum((c1 - c2) ** 2 for c1, c2 in zip(dominant_color, rgb))
                        if distance < min_distance:
                            min_distance = distance
                            color_name = name
                else:
                    color_name = "varié"
            except:
                color_name = "varié"
            
            # Determine image type based on filename
            filename = os.path.basename(image_path).lower()
            
            if any(term in filename for term in ["document", "doc", "pdf", "text", "page"]):
                image_type = "document"
            elif any(term in filename for term in ["photo", "img", "picture", "pic"]):
                image_type = "photo"
            elif any(term in filename for term in ["diagram", "chart", "graph"]):
                image_type = "diagramme"
            elif any(term in filename for term in ["logo", "icon", "symbol"]):
                image_type = "logo"
            elif any(term in filename for term in ["screenshot", "screen", "capture"]):
                image_type = "capture d'écran"
            else:
                image_type = "image"
            
            # Generate description
            description = f"Cette image est un {image_type} de {width}x{height} pixels. "
            
            if aspect_ratio > 1.2:
                description += "L'image est au format paysage. "
            elif aspect_ratio < 0.8:
                description += "L'image est au format portrait. "
            else:
                description += "L'image est approximativement carrée. "
            
            description += f"La couleur dominante semble être {color_name}. "
            
            return description
            
        except Exception as e:
            logger.error(f"Error generating image description: {str(e)}")
            return "Image non analysée en détail en raison de contraintes de ressources."
    
    def _extract_text_from_image(self, image: Image.Image) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image: PIL Image object
            
        Returns:
            Extracted text
        """
        try:
            import pytesseract
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang='fra+eng')
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return ""


class AudioProcessor:
    """Enhanced class for processing audio files"""
    
    def __init__(self):
        """Initialize audio processor"""
        self.db_manager = get_db_manager()
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize audio processing models"""
        try:
            # For now, we'll use a lightweight approach due to memory constraints
            # In production, we would use Whisper or similar models
            logger.info("Using lightweight audio processing due to resource constraints")
            
            # Set model initialized flag
            self.model_initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing audio processing models: {str(e)}")
            self.model_initialized = False
    
    def process_audio(self, audio_path: str) -> Dict[str, Any]:
        """
        Process an audio file and extract information
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary with audio analysis results
        """
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Extract basic audio properties
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(audio_path)
            
            duration_seconds = len(audio) / 1000
            channels = audio.channels
            sample_width = audio.sample_width
            frame_rate = audio.frame_rate
            
            # Generate a basic description
            description = self._generate_audio_description(audio, audio_path)
            
            # For now, we'll skip transcription due to resource constraints
            # In production, we would use Whisper or similar models
            transcription = "Transcription non disponible en raison de contraintes de ressources."
            
            # Return results
            return {
                "filename": os.path.basename(audio_path),
                "duration_seconds": duration_seconds,
                "channels": channels,
                "sample_width": sample_width,
                "frame_rate": frame_rate,
                "description": description,
                "transcription": transcription,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing audio {audio_path}: {str(e)}")
            return {
                "filename": os.path.basename(audio_path) if audio_path else "unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_audio_description(self, audio: Any, audio_path: str) -> str:
        """
        Generate a description of the audio
        
        Args:
            audio: Audio object
            audio_path: Path to the audio file
            
        Returns:
            Audio description
        """
        try:
            # Extract basic properties
            duration_seconds = len(audio) / 1000
            channels = audio.channels
            
            # Format duration
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            
            # Determine audio type based on filename
            filename = os.path.basename(audio_path).lower()
            
            if any(term in filename for term in ["voice", "speech", "talk", "conversation"]):
                audio_type = "enregistrement vocal"
            elif any(term in filename for term in ["music", "song", "track"]):
                audio_type = "musique"
            elif any(term in filename for term in ["sound", "effect", "sfx"]):
                audio_type = "effet sonore"
            else:
                audio_type = "audio"
            
            # Generate description
            description = f"Ce fichier est un {audio_type} de {minutes} minutes et {seconds} secondes. "
            
            if channels == 1:
                description += "L'audio est en mono. "
            elif channels == 2:
                description += "L'audio est en stéréo. "
            else:
                description += f"L'audio a {channels} canaux. "
            
            return description
            
        except Exception as e:
            logger.error(f"Error generating audio description: {str(e)}")
            return "Audio non analysé en détail en raison de contraintes de ressources."


class VideoProcessor:
    """Enhanced class for processing video files"""
    
    def __init__(self):
        """Initialize video processor"""
        self.db_manager = get_db_manager()
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize video processing models"""
        try:
            # For now, we'll use a lightweight approach due to memory constraints
            # In production, we would use more advanced models
            logger.info("Using lightweight video processing due to resource constraints")
            
            # Set model initialized flag
            self.model_initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing video processing models: {str(e)}")
            self.model_initialized = False
    
    def process_video(self, video_path: str) -> Dict[str, Any]:
        """
        Process a video file and extract information
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dictionary with video analysis results
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Extract basic video properties
            from moviepy.editor import VideoFileClip
            
            video = VideoFileClip(video_path)
            
            duration_seconds = video.duration
            width, height = video.size
            fps = video.fps
            
            # Generate a basic description
            description = self._generate_video_description(video, video_path)
            
            # Extract a frame for thumbnail
            thumbnail_path = None
            try:
                # Create a temporary file for the thumbnail
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    thumbnail_path = temp_file.name
                
                # Extract frame at 1 second
                frame_time = min(1.0, duration_seconds / 2)
                video.save_frame(thumbnail_path, t=frame_time)
                
                # Process the thumbnail image
                image_processor = ImageProcessor()
                thumbnail_analysis = image_processor.process_image(thumbnail_path)
                
                # Clean up
                video.close()
                
            except Exception as e:
                logger.error(f"Error extracting video thumbnail: {str(e)}")
                thumbnail_analysis = None
                if video:
                    video.close()
            
            # Return results
            result = {
                "filename": os.path.basename(video_path),
                "duration_seconds": duration_seconds,
                "width": width,
                "height": height,
                "fps": fps,
                "description": description,
                "timestamp": datetime.now().isoformat()
            }
            
            if thumbnail_analysis:
                result["thumbnail"] = {
                    "path": thumbnail_path,
                    "text": thumbnail_analysis.get("text", ""),
                    "description": thumbnail_analysis.get("description", "")
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing video {video_path}: {str(e)}")
            return {
                "filename": os.path.basename(video_path) if video_path else "unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_video_description(self, video: Any, video_path: str) -> str:
        """
        Generate a description of the video
        
        Args:
            video: Video object
            video_path: Path to the video file
            
        Returns:
            Video description
        """
        try:
            # Extract basic properties
            duration_seconds = video.duration
            width, height = video.size
            aspect_ratio = width / height
            
            # Format duration
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            
            # Determine video type based on filename
            filename = os.path.basename(video_path).lower()
            
            if any(term in filename for term in ["tutorial", "guide", "how-to"]):
                video_type = "tutoriel"
            elif any(term in filename for term in ["meeting", "conference", "presentation"]):
                video_type = "réunion"
            elif any(term in filename for term in ["demo", "demonstration"]):
                video_type = "démonstration"
            else:
                video_type = "vidéo"
            
            # Generate description
            description = f"Ce fichier est un {video_type} de {minutes} minutes et {seconds} secondes. "
            
            if width >= 1920 and height >= 1080:
                description += "La vidéo est en haute définition. "
            
            if aspect_ratio > 1.7:
                description += "La vidéo est au format écran large. "
            elif aspect_ratio < 1.3:
                description += "La vidéo est au format standard. "
            
            return description
            
        except Exception as e:
            logger.error(f"Error generating video description: {str(e)}")
            return "Vidéo non analysée en détail en raison de contraintes de ressources."


class MultimodalProcessor:
    """Main class for multimodal processing"""
    
    def __init__(self):
        """Initialize multimodal processor"""
        self.image_processor = ImageProcessor()
        self.audio_processor = AudioProcessor()
        self.video_processor = VideoProcessor()
        self.db_manager = get_db_manager()
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a file based on its type
        
        Args:
            file_path: Path to the file
            
        Returns:
            Processing results
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Determine file type
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension in config.SUPPORTED_IMAGE_TYPES:
                return self.image_processor.process_image(file_path)
            elif file_extension in config.SUPPORTED_AUDIO_TYPES:
                return self.audio_processor.process_audio(file_path)
            elif file_extension in config.SUPPORTED_VIDEO_TYPES:
                return self.video_processor.process_video(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return {
                "filename": os.path.basename(file_path) if file_path else "unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def enhance_query_with_multimodal(self, query: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhance a text query with multimodal information
        
        Args:
            query: Text query
            file_path: Path to multimodal file (optional)
            
        Returns:
            Enhanced query information
        """
        result = {
            "original_query": query,
            "enhanced_query": query,
            "has_multimodal": False,
            "timestamp": datetime.now().isoformat()
        }
        
        if not file_path:
            return result
        
        try:
            # Process the file
            file_analysis = self.process_file(file_path)
            
            # Enhance the query based on file type
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension in config.SUPPORTED_IMAGE_TYPES:
                # Extract text from image
                image_text = file_analysis.get("text", "")
                image_description = file_analysis.get("description", "")
                
                # Add image information to result
                result["has_multimodal"] = True
                result["multimodal_type"] = "image"
                result["image_analysis"] = file_analysis
                
                # Enhance query if text was found in the image
                if image_text:
                    result["enhanced_query"] = f"{query} [Texte dans l'image: {image_text}]"
                
            elif file_extension in config.SUPPORTED_AUDIO_TYPES:
                # Add audio information to result
                result["has_multimodal"] = True
                result["multimodal_type"] = "audio"
                result["audio_analysis"] = file_analysis
                
                # Enhance query if transcription is available
                transcription = file_analysis.get("transcription", "")
                if transcription and transcription != "Transcription non disponible en raison de contraintes de ressources.":
                    result["enhanced_query"] = f"{query} [Transcription audio: {transcription}]"
                
            elif file_extension in config.SUPPORTED_VIDEO_TYPES:
                # Add video information to result
                result["has_multimodal"] = True
                result["multimodal_type"] = "video"
                result["video_analysis"] = file_analysis
                
                # Enhance query with thumbnail text if available
                thumbnail = file_analysis.get("thumbnail", {})
                thumbnail_text = thumbnail.get("text", "")
                
                if thumbnail_text:
                    result["enhanced_query"] = f"{query} [Texte dans la vidéo: {thumbnail_text}]"
            
            return result
            
        except Exception as e:
            logger.error(f"Error enhancing query with multimodal: {str(e)}")
            result["error"] = str(e)
            return result


# Singleton instance
_multimodal_processor = None

def get_multimodal_processor() -> MultimodalProcessor:
    """Get or create the multimodal processor singleton"""
    global _multimodal_processor
    if _multimodal_processor is None:
        _multimodal_processor = MultimodalProcessor()
    return _multimodal_processor
