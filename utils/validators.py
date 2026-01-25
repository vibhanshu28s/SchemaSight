import re
import sqlparse
from logger_config import get_logger

logger = get_logger("sql_validator")

class SQLValidator:
    """Validates SQL queries for safety and correctness"""

    DANGEROUS_KEYWORDS = [
        'drop', 'delete', 'truncate', 'alter', 'create',
        'insert', 'update', 'grant', 'revoke', 'exec',
        'execute', 'shutdown', 'restore', 'backup'
    ]

    ALLOWED_KEYWORDS = [
        'select', 'from', 'where', 'join', 'left', 'right',
        'inner', 'outer', 'on', 'and', 'or', 'not', 'in',
        'like', 'between', 'group', 'by', 'order', 'having',
        'limit', 'offset', 'as', 'distinct', 'count', 'sum',
        'avg', 'max', 'min', 'case', 'when', 'then', 'else',
        'end', 'cast', 'coalesce', 'null'
    ]

    def validate_query(self, sql_query):
        """
        Validate SQL query for safety
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        logger.info("Validating SQL query: %s", sql_query[:100] if sql_query else "Empty query")

        if not sql_query or not isinstance(sql_query, str):
            logger.warning("Query is empty or invalid")
            return False, "Query is empty or invalid"

        normalized_query = sql_query.lower().strip()

        for keyword in self.DANGEROUS_KEYWORDS:
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, normalized_query):
                logger.warning("Dangerous operation detected: %s", keyword.upper())
                return False, f"Dangerous operation detected: {keyword.upper()}"

        if not normalized_query.startswith('select'):
            logger.warning("Query does not start with SELECT")
            return False, "Only SELECT queries are allowed"

        injection_patterns = [
            r';\s*drop',
            r';\s*delete',
            r';\s*insert',
            r';\s*update',
            r'union\s+select',
            r'--\s*$',
            r'/\*.*\*/',
            r'xp_',
            r'sp_',
            r';\s*exec',
        ]

        for pattern in injection_patterns:
            if re.search(pattern, normalized_query, re.IGNORECASE):
                logger.warning("Potential SQL injection detected")
                return False, "Potential SQL injection detected"

        try:
            parsed = sqlparse.parse(sql_query)
            if not parsed:
                logger.warning("SQL parsing returned empty result")
                return False, "Invalid SQL syntax"

            if len(parsed) > 1:
                logger.warning("Multiple statements detected")
                return False, "Multiple statements not allowed"

        except Exception as e:
            logger.exception("SQL parsing error")
            return False, f"SQL parsing error: {str(e)}"

        if normalized_query.count('select') > 5:
            logger.warning("Query too complex")
            return False, "Query too complex (too many subqueries)"

        allowed_tables = ['employees', 'departments', 'orders', 'products']
        from_pattern = r'from\s+(\w+)'
        join_pattern = r'join\s+(\w+)'

        table_references = re.findall(from_pattern, normalized_query) + re.findall(join_pattern, normalized_query)

        for table in table_references:
            if table not in allowed_tables and table not in ['e', 'd', 'o', 'p']:
                logger.warning("Unknown table referenced: %s", table)
                return False, f"Unknown table referenced: {table}"

        logger.info("SQL query validation passed")
        return True, None

    def sanitize_input(self, user_input):
        """Sanitize user input to prevent injection"""
        if not user_input:
            logger.debug("Empty input to sanitize")
            return ""

        sanitized = re.sub(r'[;\'"\\]', '', user_input)
        sanitized = re.sub(r'\s+', ' ', sanitized)
        sanitized = sanitized.strip()

        logger.debug("Sanitized input: %s", sanitized[:50])
        return sanitized

    def validate_limit(self, sql_query, max_limit=1000):
        """Ensure query has a reasonable LIMIT clause"""
        logger.debug("Validating LIMIT clause for query")
        if 'limit' not in sql_query.lower():
            logger.info("No LIMIT found, adding default LIMIT %d", max_limit)
            return f"{sql_query} LIMIT {max_limit}"

        limit_match = re.search(r'limit\s+(\d+)', sql_query.lower())
        if limit_match:
            limit_value = int(limit_match.group(1))
            if limit_value > max_limit:
                logger.info("Limit %d exceeds max, replacing with %d", limit_value, max_limit)
                return re.sub(
                    r'limit\s+\d+',
                    f'LIMIT {max_limit}',
                    sql_query,
                    flags=re.IGNORECASE
                )

        return sql_query
