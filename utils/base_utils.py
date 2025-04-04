"""
Base utilities for the multimodal RAG chatbot
"""

import os
import logging
from typing import List, Dict, Any, Union, Optional
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_file_extension(filename: str) -> str:
    """Get the file extension from a filename."""
    return os.path.splitext(filename)[1].lower()

def is_supported_file(filename: str) -> bool:
    """Check if a file is supported by the system."""
    ext = get_file_extension(filename)
    return (ext in config.SUPPORTED_DOCUMENT_TYPES or
            ext in config.SUPPORTED_IMAGE_TYPES or
            ext in config.SUPPORTED_AUDIO_TYPES or
            ext in config.SUPPORTED_VIDEO_TYPES)

def get_file_type(filename: str) -> str:
    """Get the type of file (document, image, audio, video)."""
    ext = get_file_extension(filename)
    if ext in config.SUPPORTED_DOCUMENT_TYPES:
        return "document"
    elif ext in config.SUPPORTED_IMAGE_TYPES:
        return "image"
    elif ext in config.SUPPORTED_AUDIO_TYPES:
        return "audio"
    elif ext in config.SUPPORTED_VIDEO_TYPES:
        return "video"
    else:
        return "unknown"

def create_unique_filename(original_filename: str, directory: str) -> str:
    """Create a unique filename to avoid overwriting existing files."""
    base, ext = os.path.splitext(original_filename)
    counter = 1
    new_filename = original_filename
    
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
        
    return new_filename

def safe_file_save(file_path: str, content: bytes) -> str:
    """Safely save a file to disk, ensuring the directory exists."""
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
    
    with open(file_path, 'wb') as f:
        f.write(content)
    
    return file_path

def chunk_text(text: str, chunk_size: int = config.CHUNK_SIZE, 
               chunk_overlap: int = config.CHUNK_OVERLAP) -> List[str]:
    """Split text into chunks with overlap."""
    if not text:
        return []
        
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        
        # Try to find a good breaking point (newline or period)
        if end < text_length:
            # Look for newline
            newline_pos = text.rfind('\n', start, end)
            if newline_pos > start + chunk_size // 2:
                end = newline_pos + 1
            else:
                # Look for period followed by space
                period_pos = text.rfind('. ', start, end)
                if period_pos > start + chunk_size // 2:
                    end = period_pos + 2
        
        # Add the chunk
        chunks.append(text[start:end])
        
        # Move the start position for the next chunk, considering overlap
        start = end - chunk_overlap
        
    return chunks
