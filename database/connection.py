import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config import Config
from logger_config import get_logger

logger = get_logger("database")

class DatabaseConnection:
    """Manages PostgreSQL database connections"""

    def __init__(self):
        self.config = Config
        logger.debug("DatabaseConnection initialized")

    def get_connection(self):
        """Create a new database connection"""
        logger.info("Creating database connection")
        try:
            conn = psycopg2.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                database=self.config.DB_NAME,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD
            )
            logger.info("Database connection established successfully")
            return conn
        except psycopg2.Error as e:
            logger.error("Database connection failed", exc_info=True)
            raise Exception(f"Database connection failed: {str(e)}")

    @contextmanager
    def get_cursor(self, dict_cursor=True):
        """Context manager for database cursor"""
        logger.debug("Opening database cursor | dict_cursor=%s", dict_cursor)
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor if dict_cursor else None)
        try:
            yield cursor
            conn.commit()
            logger.debug("Transaction committed")
        except Exception as e:
            conn.rollback()
            logger.error("Transaction rolled back due to error", exc_info=True)
            raise e
        finally:
            cursor.close()
            conn.close()
            logger.debug("Cursor and connection closed")

    def ensure_table_exists(self, table_name: str):
        """Check if a table exists, and create it if missing"""
        logger.debug("Checking if table '%s' exists", table_name)
        create_table_queries = {
            "departments": """
                CREATE TABLE departments (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                )
            """
        }

        if table_name not in create_table_queries:
            logger.warning("No create query defined for table '%s'", table_name)
            return

        with self.get_cursor(dict_cursor=False) as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table_name,))
            exists = cursor.fetchone()[0]

            if not exists:
                logger.info("Table '%s' does not exist. Creating now.", table_name)
                cursor.execute(create_table_queries[table_name])
                logger.info("Table '%s' created successfully", table_name)
            else:
                logger.debug("Table '%s' already exists", table_name)

    def execute_query(self, query, params=None, fetch=True, ensure_tables=None):
        """
        Execute a query and return results
        :param ensure_tables: list of tables to check/create before query
        """
        if ensure_tables:
            for table in ensure_tables:
                self.ensure_table_exists(table)

        logger.debug(
            "Executing query | fetch=%s | params_provided=%s",
            fetch, params is not None
        )
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                results = cursor.fetchall()
                logger.info("Query executed successfully | rows=%d", len(results))
                return results
            logger.info("Query executed successfully | no fetch")
            return None

    def execute_many(self, query, data):
        """Execute a query with multiple parameter sets"""
        logger.info("Executing batch query | rows=%d", len(data))
        with self.get_cursor(dict_cursor=False) as cursor:
            cursor.executemany(query, data)
        logger.info("Batch query executed successfully")

    def test_connection(self):
        """Test database connection"""
        logger.info("Testing database connection")
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error("Database connection test failed", exc_info=True)
            return False
