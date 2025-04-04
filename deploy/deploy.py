"""
Deployment script for the multimodal RAG chatbot
"""

import os
import sys
import logging
import argparse
import subprocess
from pathlib import Path

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

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        # Check Python packages
        import pymongo
        import fastapi
        import uvicorn
        import jinja2
        
        # Check MongoDB
        from pymongo import MongoClient
        client = MongoClient(host=config.MONGODB_HOST, port=config.MONGODB_PORT, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        
        logger.info("All dependencies are installed and MongoDB is running")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error checking dependencies: {str(e)}")
        return False

def start_mongodb():
    """Start MongoDB if not running"""
    try:
        # Check if MongoDB is running
        from pymongo import MongoClient
        client = MongoClient(host=config.MONGODB_HOST, port=config.MONGODB_PORT, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        logger.info("MongoDB is already running")
    except Exception:
        logger.info("Starting MongoDB...")
        try:
            subprocess.run(["sudo", "systemctl", "start", "mongod"], check=True)
            logger.info("MongoDB started successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start MongoDB: {str(e)}")
            raise

def start_web_server():
    """Start the web server"""
    try:
        logger.info("Starting web server...")
        
        # Get the path to the web app
        web_app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "app.py")
        
        # Run the web server
        subprocess.run([sys.executable, web_app_path], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start web server: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error starting web server: {str(e)}")
        raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Deploy the multimodal RAG chatbot")
    parser.add_argument("--check", action="store_true", help="Check dependencies only")
    parser.add_argument("--mongodb", action="store_true", help="Start MongoDB only")
    parser.add_argument("--web", action="store_true", help="Start web server only")
    
    args = parser.parse_args()
    
    try:
        if args.check:
            check_dependencies()
        elif args.mongodb:
            start_mongodb()
        elif args.web:
            start_web_server()
        else:
            # Run all steps
            if check_dependencies():
                start_mongodb()
                start_web_server()
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
