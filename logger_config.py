import logging
import sys

COLORS = {
    "DEBUG": "\033[94m",    
    "INFO": "\033[92m",     
    "WARNING": "\033[93m", 
    "ERROR": "\033[91m",    
    "CRITICAL": "\033[95m", 
    "RESET": "\033[0m"      
}

class ColoredFormatter(logging.Formatter):
    """Custom logging formatter with colors based on log level"""
    
    def format(self, record):
        color = COLORS.get(record.levelname, COLORS["RESET"])
        message = super().format(record)
        return f"{color}{message}{COLORS['RESET']}"

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Returns a configured logger with colored console output.
    
    Args:
        name (str): Logger name
        level (int): Logging level (default: INFO)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        formatter = ColoredFormatter(
            fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
