"""
Logging configuration for the test framework.
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class Logger:
    """Logger configuration class."""
    
    @staticmethod
    def setup_logger(name: str = "orange_hrm_tests") -> logging.Logger:
        """
        Set up and configure logger with both file and console handlers.
        
        Args:
            name: Name of the logger
            
        Returns:
            logging.Logger: Configured logger instance
        """
        # Create logs directory if it doesn't exist
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # File handler (with rotation)
        log_file = os.path.join(
            log_dir,
            f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

# Create default logger instance
logger = Logger.setup_logger() 