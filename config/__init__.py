import os
from dotenv import load_dotenv
from logger_config import get_logger

logger = get_logger("config")

load_dotenv()
logger.info("Environment variables loaded")

class Config:
    """Application configuration"""

    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'nl_search_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    logger.debug(
        "Config initialized | DB_HOST=%s | DB_PORT=%s | DB_NAME=%s | DB_USER=%s | DEBUG=%s",
        DB_HOST, DB_PORT, DB_NAME, DB_USER, DEBUG
    )

    @classmethod
    def get_db_url(cls):
        """Get database connection URL"""
        db_url = (f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}")
        logger.info("Database URL generated")
        return db_url

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        logger.info("Validating configuration")

        if not cls.OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY is missing")
            raise ValueError("OPENAI_API_KEY is required")

        if not cls.DB_PASSWORD:
            logger.error("DB_PASSWORD is missing")
            raise ValueError("DB_PASSWORD is required")

        logger.info("Configuration validation successful")
        return True
