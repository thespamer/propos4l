import json
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pythonjsonlogger import jsonlogger

class StructuredJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that adds extra fields and handles exceptions better."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        
        # Add call info
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        log_record['path'] = record.pathname
        
        # Add process/thread info
        log_record['process'] = record.process
        log_record['process_name'] = record.processName
        log_record['thread'] = record.thread
        log_record['thread_name'] = record.threadName

def get_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger instance with structured logging support.
    
    Args:
        name: Name of the logger (usually __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance with JSON formatting
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Only configure if it hasn't been configured yet
    if not logger.handlers:
        try:
            # Set log level
            level = getattr(logging, log_level.upper())
            logger.setLevel(level)
            
            # Create formatters
            json_formatter = StructuredJsonFormatter(
                '%(timestamp)s %(level)s %(name)s %(message)s'
            )
            
            # Console handler (human-readable for development)
            if os.getenv('ENVIRONMENT', 'development') == 'development':
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                ))
                logger.addHandler(console_handler)
            
            # File handlers
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True, parents=True)
            
            # Daily rotating JSON log file
            json_handler = TimedRotatingFileHandler(
                log_dir / f'{name}.json',
                when='midnight',
                interval=1,
                backupCount=30,
                encoding='utf-8'
            )
            json_handler.setFormatter(json_formatter)
            logger.addHandler(json_handler)
            
            # Size-based rotating log file for immediate access
            file_handler = RotatingFileHandler(
                log_dir / f'{name}.log',
                maxBytes=50*1024*1024,  # 50MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
            ))
            logger.addHandler(file_handler)
            
            # Set propagation to False to avoid duplicate logs
            logger.propagate = False
            
        except Exception as e:
            # Fallback to basic configuration if something goes wrong
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler(sys.stdout)]
            )
            logger.error(f'Failed to configure logger: {str(e)}')
    
    return logger

def configure_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    json_logging: bool = True,
    environment: Optional[str] = None
) -> None:
    """
    Configure global logging settings with structured logging support.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        log_format: Optional custom log format
        json_logging: Whether to use JSON structured logging
        environment: Current environment (development, staging, production)
    """
    try:
        # Set environment
        if not environment:
            environment = os.getenv('ENVIRONMENT', 'development')
        os.environ['ENVIRONMENT'] = environment
        
        # Set default format if not provided
        if not log_format:
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Create formatters
        json_formatter = StructuredJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
        text_formatter = logging.Formatter(log_format)
        
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler (human-readable in development)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            text_formatter if environment == 'development' else json_formatter
        )
        root_logger.addHandler(console_handler)
        
        # File handlers
        if log_file:
            log_dir = Path(log_file).parent
            log_dir.mkdir(exist_ok=True, parents=True)
            
            # JSON structured logging file
            if json_logging:
                json_handler = TimedRotatingFileHandler(
                    log_dir / 'app.json',
                    when='midnight',
                    interval=1,
                    backupCount=30,
                    encoding='utf-8'
                )
                json_handler.setFormatter(json_formatter)
                root_logger.addHandler(json_handler)
            
            # Regular log file
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=50*1024*1024,  # 50MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(text_formatter)
            root_logger.addHandler(file_handler)
        
        # Configure library logging
        loggers_to_quiet = {
            'sqlalchemy': logging.WARNING,
            'urllib3': logging.WARNING,
            'asyncio': logging.WARNING,
            'aiohttp': logging.WARNING,
            'PIL': logging.WARNING,
            'matplotlib': logging.WARNING,
            'boto3': logging.WARNING,
            'botocore': logging.WARNING,
            's3transfer': logging.WARNING,
            'asyncio.coroutines': logging.WARNING,
            'multipart': logging.WARNING
        }
        
        for logger_name, level in loggers_to_quiet.items():
            logging.getLogger(logger_name).setLevel(level)
        
        # Log startup message with environment info
        logging.info(
            "Logging configured successfully",
            extra={
                'environment': environment,
                'log_level': log_level,
                'json_logging': json_logging,
                'python_version': sys.version,
                'timezone': datetime.now().astimezone().tzname()
            }
        )
        
    except Exception as e:
        # Fallback to basic configuration if something goes wrong
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        logging.error(f'Failed to configure logging: {str(e)}')
