import openai
from config import Config
import json
from logger_config import get_logger

logger = get_logger("query_generator")

class QueryGenerator:
    """Generates SQL queries from natural language using OpenAI"""

    def __init__(self):
        logger.info("Initializing QueryGenerator...")
        openai.api_key = Config.OPENAI_API_KEY
        self.schema_context = self._build_schema_context()
        logger.info("QueryGenerator initialized successfully")

    def _build_schema_context(self):
        """Build schema context for the LLM"""
        logger.debug("Building schema context")
        return """
Database Schema:

1. departments table:
   - id: SERIAL PRIMARY KEY
   - name: VARCHAR(100) - Department name
   - created_at: TIMESTAMP

2. employees table:
   - id: SERIAL PRIMARY KEY
   - name: VARCHAR(100) - Employee full name
   - department_id: INT - Foreign key to departments.id
   - email: VARCHAR(255) - Email address
   - salary: DECIMAL(10,2) - Monthly salary
   - created_at: TIMESTAMP
   - name_embedding: vector(384) - Vector embedding for semantic search

3. products table:
   - id: SERIAL PRIMARY KEY
   - name: VARCHAR(100) - Product name
   - price: DECIMAL(10,2) - Price per unit
   - created_at: TIMESTAMP
   - name_embedding: vector(384) - Vector embedding for semantic search

4. orders table:
   - id: SERIAL PRIMARY KEY
   - customer_name: VARCHAR(100) - Customer name
   - employee_id: INT - Foreign key to employees.id (who handled the order)
   - order_total: DECIMAL(10,2) - Total order amount
   - order_date: DATE - Date of order
   - created_at: TIMESTAMP
   - customer_name_embedding: vector(384) - Vector embedding for semantic search

Relationships:
- employees.department_id → departments.id
- orders.employee_id → employees.id

Important Notes:
- Use JOIN operations to connect related tables
- For department names in queries, join employees with departments
- For employee names in order queries, join orders with employees
- Always use proper table aliases for clarity
- Use LIMIT clause for queries that might return many results
- Format dates as 'YYYY-MM-DD'
"""

    def generate_sql(self, user_query):
        """Generate SQL query from natural language"""
        logger.info("Generating SQL for user query: %s", user_query[:50])
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a SQL expert. Convert natural language queries to PostgreSQL SQL queries.

{self.schema_context}

Rules:
1. Return ONLY the SQL query, no explanations
2. Use proper JOINs when accessing related data
3. Add appropriate WHERE clauses for filters
4. Use LIMIT 100 for queries without specific limits
5. For aggregations, use GROUP BY appropriately
6. Always use lowercase for SQL keywords
7. Use table aliases (e.g., e for employees, d for departments)
8. Do NOT include semicolon at the end
9. For "show" or "list" queries, select relevant columns only
10. For counting/aggregations, include meaningful column names
"""
                    },
                    {"role": "user", "content": user_query}
                ],
                temperature=0,
                max_tokens=500
            )

            sql_query = response.choices[0].message.content.strip()
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            if sql_query.endswith(';'):
                sql_query = sql_query[:-1]

            logger.info("SQL generated successfully")
            return sql_query

        except Exception as e:
            logger.exception("Failed to generate SQL")
            raise Exception(f"Failed to generate SQL: {str(e)}")

    def explain_query(self, sql_query):
        """Get natural language explanation of SQL query"""
        logger.info("Generating explanation for SQL query")
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system",
                     "content": "You are a SQL expert. Explain SQL queries in simple, natural language. Be concise."},
                    {"role": "user",
                     "content": f"Explain this SQL query in one sentence:\n{sql_query}"}
                ],
                temperature=0,
                max_tokens=150
            )
            explanation = response.choices[0].message.content.strip()
            logger.info("Explanation generated successfully")
            return explanation
        except Exception as e:
            logger.warning("Could not generate explanation: %s", e)
            return "Could not generate explanation"

    def suggest_related_queries(self, user_query):
        """Suggest related queries based on user's question"""
        logger.info("Suggesting related queries for user query: %s", user_query[:50])
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system",
                     "content": f"""Based on the database schema and user query, suggest 3 related queries they might be interested in.

{self.schema_context}

Return ONLY a JSON array of 3 short query suggestions. Example: ["query 1", "query 2", "query 3"]
"""}, 
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7,
                max_tokens=200
            )
            suggestions_text = response.choices[0].message.content.strip()
            suggestions = json.loads(suggestions_text)
            logger.info("Related queries suggested successfully")
            return suggestions[:3]
        except Exception as e:
            logger.warning("Could not suggest related queries: %s", e)
            return []
