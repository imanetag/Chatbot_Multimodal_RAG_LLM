"""
Main module for the multimodal RAG chatbot
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import argparse

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from utils.base_utils import is_supported_file, get_file_type
from utils.db_manager import get_db_manager
from src.data_ingestion import get_ingestion_pipeline
from src.embedding_generator import get_embedding_generator

logger = logging.getLogger(__name__)

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

def process_file(file_path: str, generate_embeddings: bool = True) -> Dict[str, Any]:
    """
    Process a single file
    
    Args:
        file_path: Path to the file
        generate_embeddings: Whether to generate embeddings
        
    Returns:
        Processing result
    """
    # Get ingestion pipeline
    pipeline = get_ingestion_pipeline()
    
    # Ingest file
    result = pipeline.ingest_file(file_path)
    
    # Generate embeddings if requested and ingestion was successful
    if generate_embeddings and result["status"] == "success":
        if result["file_type"] == "document":
            embedding_generator = get_embedding_generator()
            embedding_ids = embedding_generator.process_document_embeddings(result["document_id"])
            result["embedding_count"] = len(embedding_ids)
    
    return result

def process_directory(directory_path: str, recursive: bool = True, 
                     generate_embeddings: bool = True) -> Dict[str, Any]:
    """
    Process all files in a directory
    
    Args:
        directory_path: Path to the directory
        recursive: Whether to process subdirectories
        generate_embeddings: Whether to generate embeddings
        
    Returns:
        Processing result
    """
    # Get ingestion pipeline
    pipeline = get_ingestion_pipeline()
    
    # Ingest directory
    result = pipeline.ingest_directory(directory_path, recursive)
    
    # Generate embeddings if requested and ingestion was successful
    if generate_embeddings and result["status"] in ["success", "partial"]:
        embedding_generator = get_embedding_generator()
        
        for file_result in result["file_results"]:
            if file_result["status"] == "success" and file_result["file_type"] == "document":
                embedding_ids = embedding_generator.process_document_embeddings(file_result["document_id"])
                file_result["embedding_count"] = len(embedding_ids)
    
    return result

def main():
    """Main entry point"""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Multimodal RAG Chatbot Data Processor")
    parser.add_argument("--file", type=str, help="Process a single file")
    parser.add_argument("--dir", type=str, help="Process a directory")
    parser.add_argument("--recursive", action="store_true", help="Process subdirectories recursively")
    parser.add_argument("--no-embeddings", action="store_true", help="Skip embedding generation")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    logger.info("Starting multimodal RAG chatbot data processor")
    
    # Process file or directory
    if args.file:
        if os.path.isfile(args.file):
            logger.info(f"Processing file: {args.file}")
            result = process_file(args.file, not args.no_embeddings)
            logger.info(f"File processing result: {result}")
        else:
            logger.error(f"File not found: {args.file}")
    elif args.dir:
        if os.path.isdir(args.dir):
            logger.info(f"Processing directory: {args.dir}")
            result = process_directory(args.dir, args.recursive, not args.no_embeddings)
            logger.info(f"Directory processing result: {result}")
        else:
            logger.error(f"Directory not found: {args.dir}")
    else:
        logger.error("No file or directory specified")
        parser.print_help()
    
    logger.info("Multimodal RAG chatbot data processor completed")

if __name__ == "__main__":
    main()
