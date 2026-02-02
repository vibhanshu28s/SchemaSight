from sentence_transformers import SentenceTransformer
import numpy as np
from database.connection import DatabaseConnection
from logger_config import get_logger

logger = get_logger("embedding_service")

class EmbeddingService:
    """Service for generating and managing vector embeddings"""

    def __init__(self):
        logger.info("Initializing EmbeddingService...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # openai.api_key = Config.OPENAI_API_KEY
        # self.model = "text-embedding-3-small"
        # self.dimensions = 384
        self.db = DatabaseConnection()
        logger.info("EmbeddingService initialized successfully")

    def generate_embedding(self, text):
        """Generate embedding for a single text"""
        if not text:
            logger.warning("Empty text received for embedding")
            return None
        embedding = self.model.encode(text, convert_to_numpy=True)
        logger.debug("Generated embedding for text: %s", text[:50])
        return embedding.tolist()

    def generate_embeddings_batch(self, texts):
        """Generate embeddings for multiple texts"""
        logger.info("Generating embeddings batch | size=%d", len(texts))
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        logger.info("Batch embeddings generated successfully")
        return [emb.tolist() for emb in embeddings]

    def populate_employee_embeddings(self):
        """Generate and store embeddings for all employees"""
        logger.info("Populating employee embeddings...")
        query = "SELECT id, name FROM employees WHERE name_embedding IS NULL"
        employees = self.db.execute_query(query)

        if not employees:
            logger.info("All employee embeddings already generated")
            return

        logger.info("Generating embeddings for %d employees", len(employees))
        names = [emp['name'] for emp in employees]
        embeddings = self.generate_embeddings_batch(names)

        update_query = """
            UPDATE employees 
            SET name_embedding = %s::vector 
            WHERE id = %s
        """
        data = [(str(emb), emp['id']) for emb, emp in zip(embeddings, employees)]
        self.db.execute_many(update_query, data)
        logger.info("✓ Generated %d employee embeddings", len(employees))

    def populate_product_embeddings(self):
        """Generate and store embeddings for all products"""
        logger.info("Populating product embeddings...")
        query = "SELECT id, name FROM products WHERE name_embedding IS NULL"
        products = self.db.execute_query(query)

        if not products:
            logger.info("All product embeddings already generated")
            return

        logger.info("Generating embeddings for %d products", len(products))
        names = [prod['name'] for prod in products]
        embeddings = self.generate_embeddings_batch(names)

        update_query = """
            UPDATE products 
            SET name_embedding = %s::vector 
            WHERE id = %s
        """
        data = [(str(emb), prod['id']) for emb, prod in zip(embeddings, products)]
        self.db.execute_many(update_query, data)
        logger.info("✓ Generated %d product embeddings", len(products))

    def populate_order_embeddings(self):
        """Generate and store embeddings for all orders (customer names)"""
        logger.info("Populating order embeddings...")
        query = "SELECT id, customer_name FROM orders WHERE customer_name_embedding IS NULL"
        orders = self.db.execute_query(query)

        if not orders:
            logger.info("All order embeddings already generated")
            return

        logger.info("Generating embeddings for %d orders", len(orders))
        names = [order['customer_name'] for order in orders]
        embeddings = self.generate_embeddings_batch(names)

        update_query = """
            UPDATE orders 
            SET customer_name_embedding = %s::vector 
            WHERE id = %s
        """
        data = [(str(emb), order['id']) for emb, order in zip(embeddings, orders)]
        self.db.execute_many(update_query, data)
        logger.info("✓ Generated %d order embeddings", len(orders))

    def populate_all_embeddings(self):
        """Generate embeddings for all tables"""
        logger.info("Populating vector embeddings for all tables...")
        self.populate_employee_embeddings()
        self.populate_product_embeddings()
        self.populate_order_embeddings()
        logger.info("All embeddings generated successfully")

    def search_similar_products(self, query_text, limit=5):
        """Search for products similar to query text"""
        logger.info("Searching similar products for query: %s", query_text[:50])
        query_embedding = self.generate_embedding(query_text)

        sql = """
            SELECT id, name, price, 
                   1 - (name_embedding <=> %s::vector) as similarity
            FROM products
            WHERE name_embedding IS NOT NULL
            ORDER BY name_embedding <=> %s::vector
            LIMIT %s
        """

        results = self.db.execute_query(
            sql, 
            (str(query_embedding), str(query_embedding), limit)
        )
        logger.info("Found %d similar products", len(results))
        return results

    def search_similar_employees(self, query_text, limit=5):
        """Search for employees similar to query text"""
        logger.info("Searching similar employees for query: %s", query_text[:50])
        query_embedding = self.generate_embedding(query_text)

        sql = """
            SELECT e.id, e.name, e.email, e.salary, d.name as department,
                   1 - (e.name_embedding <=> %s::vector) as similarity
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE e.name_embedding IS NOT NULL
            ORDER BY e.name_embedding <=> %s::vector
            LIMIT %s
        """

        results = self.db.execute_query(
            sql, 
            (str(query_embedding), str(query_embedding), limit)
        )
        logger.info("Found %d similar employees", len(results))
        return results
