"""
Monitoring and logging module for the multimodal RAG chatbot
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

# Configure logging
logger = logging.getLogger(__name__)

class ChatbotMonitor:
    """Class for monitoring and logging chatbot activity"""
    
    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize chatbot monitor
        
        Args:
            log_dir: Directory for log files (optional)
        """
        # Set log directory
        if log_dir:
            self.log_dir = log_dir
        else:
            self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        
        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Set up log files
        self.query_log_path = os.path.join(self.log_dir, "queries.log")
        self.error_log_path = os.path.join(self.log_dir, "errors.log")
        self.performance_log_path = os.path.join(self.log_dir, "performance.log")
        
        # Set up loggers
        self._setup_loggers()
        
        logger.info(f"Chatbot monitor initialized with log directory: {self.log_dir}")
    
    def _setup_loggers(self):
        """Set up specialized loggers"""
        # Query logger
        self.query_logger = logging.getLogger("query_logger")
        self.query_logger.setLevel(logging.INFO)
        query_handler = logging.FileHandler(self.query_log_path)
        query_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.query_logger.addHandler(query_handler)
        
        # Error logger
        self.error_logger = logging.getLogger("error_logger")
        self.error_logger.setLevel(logging.ERROR)
        error_handler = logging.FileHandler(self.error_log_path)
        error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.error_logger.addHandler(error_handler)
        
        # Performance logger
        self.performance_logger = logging.getLogger("performance_logger")
        self.performance_logger.setLevel(logging.INFO)
        performance_handler = logging.FileHandler(self.performance_log_path)
        performance_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.performance_logger.addHandler(performance_handler)
    
    def log_query(self, query: str, response: str, metadata: Dict[str, Any]):
        """
        Log a query and its response
        
        Args:
            query: User query
            response: Chatbot response
            metadata: Additional metadata
        """
        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": response,
                "metadata": metadata
            }
            
            # Log as JSON
            self.query_logger.info(json.dumps(log_entry))
            
        except Exception as e:
            logger.error(f"Error logging query: {str(e)}")
    
    def log_error(self, error_message: str, context: Dict[str, Any]):
        """
        Log an error
        
        Args:
            error_message: Error message
            context: Error context
        """
        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "error": error_message,
                "context": context
            }
            
            # Log as JSON
            self.error_logger.error(json.dumps(log_entry))
            
        except Exception as e:
            logger.error(f"Error logging error: {str(e)}")
    
    def log_performance(self, operation: str, duration_ms: float, metadata: Dict[str, Any]):
        """
        Log performance metrics
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            metadata: Additional metadata
        """
        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "duration_ms": duration_ms,
                "metadata": metadata
            }
            
            # Log as JSON
            self.performance_logger.info(json.dumps(log_entry))
            
        except Exception as e:
            logger.error(f"Error logging performance: {str(e)}")
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent queries from the log
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of recent queries
        """
        try:
            queries = []
            
            # Read query log file
            if os.path.exists(self.query_log_path):
                with open(self.query_log_path, 'r') as f:
                    lines = f.readlines()
                    
                    # Parse JSON entries
                    for line in reversed(lines):
                        try:
                            # Extract JSON part (after timestamp)
                            json_str = line.split(' - ', 1)[1]
                            entry = json.loads(json_str)
                            queries.append(entry)
                            
                            if len(queries) >= limit:
                                break
                        except:
                            continue
            
            return queries
            
        except Exception as e:
            logger.error(f"Error getting recent queries: {str(e)}")
            return []
    
    def get_error_stats(self) -> Dict[str, Any]:
        """
        Get error statistics
        
        Returns:
            Dictionary with error statistics
        """
        try:
            stats = {
                "total_errors": 0,
                "recent_errors": []
            }
            
            # Read error log file
            if os.path.exists(self.error_log_path):
                with open(self.error_log_path, 'r') as f:
                    lines = f.readlines()
                    
                    stats["total_errors"] = len(lines)
                    
                    # Parse recent JSON entries
                    for line in reversed(lines[:10]):
                        try:
                            # Extract JSON part (after timestamp and level)
                            json_str = line.split(' - ERROR - ', 1)[1]
                            entry = json.loads(json_str)
                            stats["recent_errors"].append(entry)
                        except:
                            continue
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting error stats: {str(e)}")
            return {"total_errors": 0, "recent_errors": []}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics
        
        Returns:
            Dictionary with performance statistics
        """
        try:
            stats = {
                "operations": {},
                "average_durations": {}
            }
            
            # Read performance log file
            if os.path.exists(self.performance_log_path):
                with open(self.performance_log_path, 'r') as f:
                    lines = f.readlines()
                    
                    # Parse JSON entries
                    for line in lines:
                        try:
                            # Extract JSON part (after timestamp)
                            json_str = line.split(' - ', 1)[1]
                            entry = json.loads(json_str)
                            
                            operation = entry.get("operation")
                            duration = entry.get("duration_ms")
                            
                            if operation and duration:
                                if operation not in stats["operations"]:
                                    stats["operations"][operation] = []
                                
                                stats["operations"][operation].append(duration)
                        except:
                            continue
                    
                    # Calculate averages
                    for operation, durations in stats["operations"].items():
                        if durations:
                            stats["average_durations"][operation] = sum(durations) / len(durations)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting performance stats: {str(e)}")
            return {"operations": {}, "average_durations": {}}


# Singleton instance
_chatbot_monitor = None

def get_chatbot_monitor() -> ChatbotMonitor:
    """Get or create the chatbot monitor singleton"""
    global _chatbot_monitor
    if _chatbot_monitor is None:
        _chatbot_monitor = ChatbotMonitor()
    return _chatbot_monitor
