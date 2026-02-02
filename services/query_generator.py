from groq import Groq
from config import Config
import json
from logger_config import get_logger

logger = get_logger("query_generator")


class QueryGenerator:
    """Generates SQL queries from natural language using Groq (Llama 3.3)"""

    def __init__(self):
        logger.info("Initializing QueryGenerator with Groq...")
        # Groq uses a client-based approach similar to OpenAI
        self.client = Groq(api_key=Config.GROQ_API_KEY)

        # Recommended high-performance model
        self.model = "llama-3.3-70b-versatile"
        self.schema_context = self._build_schema_context()
        logger.info(f"QueryGenerator initialized with {self.model}")

    def _build_schema_context(self):
        """Build schema context for the LLM (Grounding)"""
        logger.debug("Building schema context")
        return """
Database Schema:
1. departments table: id, name, created_at
2. employees table: id, name, department_id, email, salary, created_at, name_embedding
3. products table: id, name, price, created_at, name_embedding
4. orders table: id, customer_name, employee_id, order_total, order_date, created_at, customer_name_embedding

Relationships:
- employees.department_id → departments.id
- orders.employee_id → employees.id
"""

    def generate_sql(self, user_query):
        """Generate SQL query from natural language using Groq"""
        logger.info("Generating SQL for user query: %s", user_query[:50])

        system_instruction = f"""You are a SQL expert. Convert natural language queries to PostgreSQL SQL queries.
        {self.schema_context}
        Rules:
        1. Return ONLY the raw SQL query, no explanations, no markdown, no backticks
        2. Use proper JOINs and lowercase keywords
        3. Use table aliases (e.g., e for employees)
        4. Use LIMIT 100 if no limit is specified
        5. Do NOT include a semicolon at the end
        """

        try:
            # Groq chat completion call
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_query}
                ],
                model=self.model,
                temperature=0  # Keeping it deterministic for SQL
            )

            # Accessing the content from Groq's response object
            sql_query = chat_completion.choices[0].message.content.strip()

            # Additional cleanup for hallucinations
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            if sql_query.endswith(';'):
                sql_query = sql_query[:-1]

            logger.info("SQL generated successfully by Groq")
            return sql_query

        except Exception as e:
            logger.exception("Failed to generate SQL with Groq")
            raise Exception(f"Groq generation failed: {str(e)}")

    def explain_query(self, sql_query):
        """Get natural language explanation using Groq"""
        logger.info("Generating explanation for SQL query")
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Explain SQL queries concisely in one sentence."},
                    {"role": "user", "content": f"Explain this: {sql_query}"}
                ],
                model=self.model
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning("Could not generate explanation: %s", e)
            return "Could not generate explanation"

    def suggest_related_queries(self, user_query):
        """Suggest 3 related queries using Groq's JSON mode"""
        logger.info("Suggesting related queries")
        prompt = f"""Based on this schema: {self.schema_context}
        Suggest 3 related natural language queries for: "{user_query}"
        Return ONLY a JSON array of strings. Example: ["query 1", "query 2", "query 3"]"""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                # Groq can enforce JSON output if specified in the prompt
                response_format={"type": "json_object"}
            )
            suggestions_text = response.choices[0].message.content.strip()
            # Groq's JSON mode returns an object, we extract our array
            data = json.loads(suggestions_text)
            # If the model wraps it in a key like 'queries', adjust accordingly
            return list(data.values())[0][:3] if isinstance(data, dict) else data[:3]
        except Exception as e:
            logger.warning("Could not suggest related queries: %s", e)
            return []