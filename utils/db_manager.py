"""
MongoDB database connection and operations for the multimodal RAG chatbot
"""

import os
import sys
from typing import Dict, List, Any, Optional, Union
import logging
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import gridfs

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

logger = logging.getLogger(__name__)

class MongoDBManager:
    """Manager for MongoDB operations"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(
                host=config.MONGODB_HOST,
                port=config.MONGODB_PORT
            )
            self.db = self.client[config.MONGODB_DB]
            self.fs = gridfs.GridFS(self.db)
            
            # Initialize collections
            self.documents = self.db[config.MONGODB_COLLECTION_DOCUMENTS]
            self.chunks = self.db[config.MONGODB_COLLECTION_CHUNKS]
            self.embeddings = self.db[config.MONGODB_COLLECTION_EMBEDDINGS]
            self.images = self.db[config.MONGODB_COLLECTION_IMAGES]
            self.audio = self.db[config.MONGODB_COLLECTION_AUDIO]
            self.video = self.db[config.MONGODB_COLLECTION_VIDEO]
            
            # Create indexes
            self._create_indexes()
            
            logger.info("MongoDB connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def _create_indexes(self):
        """Create necessary indexes for efficient querying"""
        # Document collection indexes
        self.documents.create_index("filename", unique=True)
        self.documents.create_index("file_type")
        self.documents.create_index("created_at")
        
        # Chunk collection indexes
        self.chunks.create_index("document_id")
        self.chunks.create_index("chunk_index")
        
        # Embedding collection indexes
        self.embeddings.create_index("chunk_id")
        self.embeddings.create_index("document_id")
        
        # Media collection indexes
        self.images.create_index("filename", unique=True)
        self.audio.create_index("filename", unique=True)
        self.video.create_index("filename", unique=True)
    
    def store_file(self, filename: str, content: bytes, metadata: Dict[str, Any]) -> str:
        """
        Store a file in GridFS
        
        Args:
            filename: Name of the file
            content: Binary content of the file
            metadata: Additional metadata for the file
            
        Returns:
            GridFS file ID
        """
        try:
            file_id = self.fs.put(content, filename=filename, metadata=metadata)
            logger.info(f"File {filename} stored in GridFS with ID {file_id}")
            return str(file_id)
        except Exception as e:
            logger.error(f"Failed to store file {filename} in GridFS: {str(e)}")
            raise
    
    def get_file(self, file_id: str) -> Optional[bytes]:
        """
        Retrieve a file from GridFS
        
        Args:
            file_id: GridFS file ID
            
        Returns:
            File content as bytes or None if not found
        """
        try:
            if self.fs.exists(file_id):
                grid_out = self.fs.get(file_id)
                return grid_out.read()
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve file with ID {file_id} from GridFS: {str(e)}")
            return None
    
    def store_document_metadata(self, document_data: Dict[str, Any]) -> str:
        """
        Store document metadata in the documents collection
        
        Args:
            document_data: Document metadata
            
        Returns:
            Document ID
        """
        try:
            result = self.documents.insert_one(document_data)
            logger.info(f"Document metadata stored with ID {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to store document metadata: {str(e)}")
            raise
    
    def store_chunks(self, chunks_data: List[Dict[str, Any]]) -> List[str]:
        """
        Store document chunks in the chunks collection
        
        Args:
            chunks_data: List of chunk data dictionaries
            
        Returns:
            List of chunk IDs
        """
        try:
            result = self.chunks.insert_many(chunks_data)
            chunk_ids = [str(id) for id in result.inserted_ids]
            logger.info(f"Stored {len(chunk_ids)} chunks")
            return chunk_ids
        except Exception as e:
            logger.error(f"Failed to store chunks: {str(e)}")
            raise
    
    def store_embeddings(self, embeddings_data: List[Dict[str, Any]]) -> List[str]:
        """
        Store embeddings in the embeddings collection
        
        Args:
            embeddings_data: List of embedding data dictionaries
            
        Returns:
            List of embedding IDs
        """
        try:
            result = self.embeddings.insert_many(embeddings_data)
            embedding_ids = [str(id) for id in result.inserted_ids]
            logger.info(f"Stored {len(embedding_ids)} embeddings")
            return embedding_ids
        except Exception as e:
            logger.error(f"Failed to store embeddings: {str(e)}")
            raise
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document metadata by ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Document metadata or None if not found
        """
        try:
            from bson.objectid import ObjectId
            return self.documents.find_one({"_id": ObjectId(document_id)})
        except Exception as e:
            logger.error(f"Failed to get document with ID {document_id}: {str(e)}")
            return None
    
    def get_chunks_by_document_id(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a document
        
        Args:
            document_id: Document ID
            
        Returns:
            List of chunks
        """
        try:
            from bson.objectid import ObjectId
            return list(self.chunks.find({"document_id": document_id}))
        except Exception as e:
            logger.error(f"Failed to get chunks for document {document_id}: {str(e)}")
            return []
    
    def get_embeddings_by_document_id(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Get all embeddings for a document
        
        Args:
            document_id: Document ID
            
        Returns:
            List of embeddings
        """
        try:
            return list(self.embeddings.find({"document_id": document_id}))
        except Exception as e:
            logger.error(f"Failed to get embeddings for document {document_id}: {str(e)}")
            return []
    
    def close(self):
        """Close the MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("MongoDB connection closed")

# Singleton instance
_db_manager = None

def get_db_manager() -> MongoDBManager:
    """Get or create the MongoDB manager singleton"""
    global _db_manager
    if _db_manager is None:
        _db_manager = MongoDBManager()
    return _db_manager
