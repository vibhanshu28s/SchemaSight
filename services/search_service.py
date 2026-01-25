from database.connection import DatabaseConnection
from services.embedding_service import EmbeddingService
from services.query_generator import QueryGenerator
from utils.validators import SQLValidator
from logger_config import get_logger
import re

logger = get_logger("search_service")

class SearchService:
    """Orchestrates search operations combining SQL and vector search"""

    def __init__(self):
        logger.info("Initializing SearchService...")
        self.db = DatabaseConnection()
        self.embedding_service = EmbeddingService()
        self.query_generator = QueryGenerator()
        self.validator = SQLValidator()
        logger.info("SearchService initialized successfully")

    def search(self, user_query):
        """
        Main search method that combines SQL generation and vector search
        """
        logger.info("Received search query: %s", user_query[:50])
        result = {
            'success': False,
            'results': [],
            'sql_query': None,
            'explanation': None,
            'search_type': 'sql',
            'error': None
        }

        try:
            is_semantic = self._is_semantic_query(user_query)
            logger.debug("Is semantic query: %s", is_semantic)

            if is_semantic:
                logger.info("Performing semantic search")
                return self._semantic_search(user_query)
            else:
                logger.info("Performing SQL-based search")
                return self._sql_search(user_query)

        except Exception as e:
            logger.exception("Search failed")
            result['error'] = str(e)
            return result

    def _is_semantic_query(self, query):
        """Determine if query should use semantic search"""
        semantic_keywords = [
            'similar', 'like', 'related to', 'find products',
            'search for', 'looking for', 'type of'
        ]
        query_lower = query.lower()
        is_semantic = any(keyword in query_lower for keyword in semantic_keywords)
        logger.debug("Semantic query check for '%s': %s", query[:50], is_semantic)
        return is_semantic

    def _sql_search(self, user_query):
        """Execute search using SQL generation"""
        logger.info("Executing SQL search for query: %s", user_query[:50])
        result = {
            'success': False,
            'results': [],
            'sql_query': None,
            'explanation': None,
            'search_type': 'sql',
            'error': None
        }

        try:
            sql_query = self.query_generator.generate_sql(user_query)
            result['sql_query'] = sql_query
            logger.debug("Generated SQL: %s", sql_query[:100])

            is_valid, error_msg = self.validator.validate_query(sql_query)
            if not is_valid:
                result['error'] = f"Invalid query: {error_msg}"
                logger.warning("SQL validation failed: %s", error_msg)
                return result

            results = self.db.execute_query(sql_query)
            result['results'] = [dict(row) for row in results]
            result['success'] = True
            logger.info("SQL query executed successfully | rows=%d", len(results))

            result['explanation'] = self.query_generator.explain_query(sql_query)

        except Exception as e:
            logger.exception("SQL search failed")
            result['error'] = f"Query execution failed: {str(e)}"

        return result

    def _semantic_search(self, user_query):
        """Execute semantic search using vector embeddings"""
        logger.info("Executing semantic search for query: %s", user_query[:50])
        result = {
            'success': False,
            'results': [],
            'sql_query': None,
            'explanation': f"Performing semantic search for: {user_query}",
            'search_type': 'semantic',
            'error': None
        }

        try:
            if 'product' in user_query.lower():
                results = self.embedding_service.search_similar_products(user_query, limit=10)
                result['explanation'] = "Searching for similar products using AI embeddings"
            elif 'employee' in user_query.lower():
                results = self.embedding_service.search_similar_employees(user_query, limit=10)
                result['explanation'] = "Searching for similar employees using AI embeddings"
            else:
                results = self.embedding_service.search_similar_products(user_query, limit=10)
                result['explanation'] = "Performing semantic search across products"

            result['results'] = [dict(row) for row in results]
            result['success'] = True
            logger.info("Semantic search completed | results=%d", len(results))

        except Exception as e:
            logger.exception("Semantic search failed")
            result['error'] = f"Semantic search failed: {str(e)}"

        return result

    def hybrid_search(self, user_query):
        """
        Perform hybrid search combining both SQL and vector search
        """
        logger.info("Performing hybrid search for query: %s", user_query[:50])
        sql_result = self._sql_search(user_query)
        semantic_result = self._semantic_search(user_query)

        combined_results = []
        seen_ids = set()

        for item in sql_result.get('results', []):
            item_id = item.get('id')
            if item_id and item_id not in seen_ids:
                combined_results.append(item)
                seen_ids.add(item_id)

        for item in semantic_result.get('results', []):
            item_id = item.get('id')
            if item_id and item_id not in seen_ids:
                combined_results.append(item)
                seen_ids.add(item_id)

        logger.info("Hybrid search completed | combined results=%d", len(combined_results))
        return {
            'success': True,
            'results': combined_results,
            'sql_query': sql_result.get('sql_query'),
            'explanation': 'Hybrid search combining SQL and semantic similarity',
            'search_type': 'hybrid',
            'error': None
        }
