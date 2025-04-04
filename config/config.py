"""
Configuration file for the multimodal RAG chatbot
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
CONFIG_DIR = os.path.join(BASE_DIR, "config")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# MongoDB configuration
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "rag_chatbot"
MONGODB_COLLECTION_DOCUMENTS = "documents"
MONGODB_COLLECTION_CHUNKS = "chunks"
MONGODB_COLLECTION_EMBEDDINGS = "embeddings"
MONGODB_COLLECTION_IMAGES = "images"
MONGODB_COLLECTION_AUDIO = "audio"
MONGODB_COLLECTION_VIDEO = "video"

# Document processing
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MAX_DOCUMENT_SIZE_MB = 50

# Embedding models
TEXT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
IMAGE_EMBEDDING_MODEL = "clip-ViT-B-32"

# Vector search
VECTOR_SIMILARITY_THRESHOLD = 0.7
MAX_RESULTS = 10

# LLM configuration
LLM_MODEL_PATH = os.path.join(MODELS_DIR, "llm_model")
LLM_MODEL_TYPE = "gemma"  # or "deepseek"

# Web interface
WEB_HOST = "0.0.0.0"
WEB_PORT = 8000
UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(BASE_DIR, "chatbot.log")

# Supported file types
SUPPORTED_DOCUMENT_TYPES = [
    ".pdf", ".docx", ".pptx", ".xlsx", ".txt", ".md", ".csv", ".json", ".html", ".one"
]
SUPPORTED_IMAGE_TYPES = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
SUPPORTED_AUDIO_TYPES = [".mp3", ".wav", ".ogg", ".flac", ".m4a"]
SUPPORTED_VIDEO_TYPES = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
