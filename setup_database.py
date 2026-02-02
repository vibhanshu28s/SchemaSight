"""Database setup script Creates database, tables, and populates sample data with embeddings"""

import os
import psycopg2
import sqlparse
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import Config
from database.connection import DatabaseConnection
from services.embedding_service import EmbeddingService
from logger_config import get_logger

logger = get_logger("setup_database")


def create_database():
    """Create the database if it doesn't exist"""
    logger.info("Setting up database...")

    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (Config.DB_NAME,)
        )

        if not cursor.fetchone():
            cursor.execute(f'CREATE DATABASE "{Config.DB_NAME}"')
            logger.info("Database '%s' created", Config.DB_NAME)
        else:
            logger.info("Database '%s' already exists", Config.DB_NAME)

        cursor.close()
        conn.close()

    except Exception:
        logger.exception("Error creating database")
        raise

def ensure_pgvector_extension():
    logger.info("Ensuring pgvector extension exists...")

    logger.info(
        f"Connecting for pgvector → "
        f"host={Config.DB_HOST}, "
        f"port={Config.DB_PORT}, "
        f"db={Config.DB_NAME}, "
        f"user={Config.DB_USER}"
    )

    conn = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        dbname=Config.DB_NAME
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    cursor.execute("SHOW server_version;")
    logger.info(f"Connected Postgres version: {cursor.fetchone()}")

    cursor.execute("SHOW data_directory;")
    logger.info(f"Postgres data directory: {cursor.fetchone()}")

    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    cursor.close()
    conn.close()

def run_sql_file(filename):
    """Execute SQL commands from a file"""
    db = DatabaseConnection()
    filepath = os.path.join("database", filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"SQL file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        sql_content = f.read()

    statements = sqlparse.split(sql_content)

    try:
        with db.get_cursor(dict_cursor=False) as cursor:
            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt)

        logger.info("Executed SQL file: %s (%d statements)", filename, len(statements))

    except Exception:
        logger.exception("Error executing SQL file: %s", filename)
        raise


def main():
    logger.info("=" * 50)
    logger.info("DATABASE SETUP STARTED")
    logger.info("=" * 50)

    try:
        Config.validate()
        logger.info("Configuration validated successfully")

        create_database()

        ensure_pgvector_extension()

        logger.info("Creating database schema...")
        run_sql_file("schema.sql")

        logger.info("Inserting sample data...")
        run_sql_file("seed_data.sql")

        logger.info("Generating AI embeddings...")
        embedding_service = EmbeddingService()
        embedding_service.populate_all_embeddings()

        logger.info("=" * 50)
        logger.info("DATABASE SETUP COMPLETE!")
        logger.info("=" * 50)

    except Exception:
        logger.error("=" * 50)
        logger.error("SETUP FAILED")
        logger.error("=" * 50)
        logger.exception("Error during database setup")
        exit(1)


if __name__ == "__main__":
    main()
