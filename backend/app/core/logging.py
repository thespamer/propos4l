import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

def get_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Name of the logger (usually __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Only configure if it hasn't been configured yet
    if not logger.handlers:
        logger.setLevel(getattr(logging, log_level))
        
        # Create formatters
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_dir / "propos4l.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Set propagation to False to avoid duplicate logs
        logger.propagate = False
    
    return logger

def configure_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """
    Configure global logging settings.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        log_format: Optional custom log format
    """
    # Set default format if not provided
    if not log_format:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Basic configuration
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Add file handler if log file specified
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)
    
    # Configure library logging
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Log startup message
    logging.info("Logging configured successfully")
