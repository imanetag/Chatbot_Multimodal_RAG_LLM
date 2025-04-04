"""
Data ingestion pipeline for the multimodal RAG chatbot
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import tempfile

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
from utils.base_utils import get_file_type, is_supported_file, create_unique_filename
from utils.db_manager import get_db_manager
from src.document_processor import get_processor

logger = logging.getLogger(__name__)

class DataIngestionPipeline:
    """Main class for data ingestion pipeline"""
    
    def __init__(self):
        """Initialize data ingestion pipeline"""
        self.db_manager = get_db_manager()
    
    def ingest_file(self, file_path: str, file_content: bytes = None, 
                   metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Ingest a file into the system
        
        Args:
            file_path: Path to the file
            file_content: Binary content of the file (optional)
            metadata: Additional metadata for the file (optional)
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            # Validate file
            if not is_supported_file(file_path):
                raise ValueError(f"Unsupported file type: {file_path}")
            
            # Read file content if not provided
            if file_content is None:
                with open(file_path, 'rb') as f:
                    file_content = f.read()
            
            # Initialize metadata if not provided
            if metadata is None:
                metadata = {}
            
            # Add basic metadata
            metadata.update({
                "original_filename": os.path.basename(file_path),
                "ingestion_time": datetime.now().isoformat()
            })
            
            # Get file type
            file_type = get_file_type(file_path)
            
            # Get appropriate processor
            processor = get_processor(file_type)
            
            # Process file based on type
            if file_type == "document":
                document_id = processor.process_document(file_path, file_content, metadata)
                return {
                    "status": "success",
                    "file_type": file_type,
                    "document_id": document_id,
                    "message": f"Document {os.path.basename(file_path)} ingested successfully"
                }
            elif file_type == "image":
                image_id = processor.process_image(file_path, file_content, metadata)
                return {
                    "status": "success",
                    "file_type": file_type,
                    "image_id": image_id,
                    "message": f"Image {os.path.basename(file_path)} ingested successfully"
                }
            elif file_type == "audio":
                audio_id = processor.process_audio(file_path, file_content, metadata)
                return {
                    "status": "success",
                    "file_type": file_type,
                    "audio_id": audio_id,
                    "message": f"Audio {os.path.basename(file_path)} ingested successfully"
                }
            elif file_type == "video":
                video_id = processor.process_video(file_path, file_content, metadata)
                return {
                    "status": "success",
                    "file_type": file_type,
                    "video_id": video_id,
                    "message": f"Video {os.path.basename(file_path)} ingested successfully"
                }
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        
        except Exception as e:
            logger.error(f"Error ingesting file {file_path}: {str(e)}")
            return {
                "status": "error",
                "file_path": file_path,
                "error": str(e),
                "message": f"Failed to ingest file {os.path.basename(file_path)}"
            }
    
    def ingest_directory(self, directory_path: str, recursive: bool = True,
                        metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Ingest all supported files in a directory
        
        Args:
            directory_path: Path to the directory
            recursive: Whether to recursively process subdirectories
            metadata: Additional metadata for all files
            
        Returns:
            Dictionary with ingestion results
        """
        if not os.path.isdir(directory_path):
            return {
                "status": "error",
                "error": f"Directory not found: {directory_path}",
                "message": "Failed to ingest directory"
            }
        
        results = {
            "status": "success",
            "directory": directory_path,
            "files_processed": 0,
            "files_succeeded": 0,
            "files_failed": 0,
            "file_results": []
        }
        
        # Initialize metadata if not provided
        if metadata is None:
            metadata = {}
        
        # Add directory info to metadata
        dir_metadata = metadata.copy()
        dir_metadata.update({
            "source_directory": directory_path,
            "ingestion_batch": datetime.now().isoformat()
        })
        
        # Process files
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip unsupported files
                if not is_supported_file(file_path):
                    continue
                
                # Ingest file
                file_result = self.ingest_file(file_path, metadata=dir_metadata)
                results["files_processed"] += 1
                
                if file_result["status"] == "success":
                    results["files_succeeded"] += 1
                else:
                    results["files_failed"] += 1
                
                results["file_results"].append(file_result)
            
            # If not recursive, break after processing the top directory
            if not recursive:
                break
        
        # Update overall status
        if results["files_failed"] > 0 and results["files_succeeded"] == 0:
            results["status"] = "error"
            results["message"] = f"All {results['files_processed']} files failed to ingest"
        elif results["files_failed"] > 0:
            results["status"] = "partial"
            results["message"] = f"Ingested {results['files_succeeded']} files, {results['files_failed']} files failed"
        else:
            results["message"] = f"Successfully ingested {results['files_succeeded']} files"
        
        return results


# Singleton instance
_ingestion_pipeline = None

def get_ingestion_pipeline() -> DataIngestionPipeline:
    """Get or create the data ingestion pipeline singleton"""
    global _ingestion_pipeline
    if _ingestion_pipeline is None:
        _ingestion_pipeline = DataIngestionPipeline()
    return _ingestion_pipeline
