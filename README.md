# SchemaSight
SchemaSight is a prototype that bridges the gap between natural language and PostgreSQL.

---

#  SchemaSight: RAG-Powered Text-to-SQL

**SchemaSight** is a prototype that bridges the gap between natural language and PostgreSQL. It uses Retrieval-Augmented Generation (RAG) to ground LLM queries in a specific database schema, significantly reducing hallucinations and ensuring SQL accuracy.

##  Features

* **Semantic Schema Retrieval**: Uses **FAISS** to retrieve only the relevant table and column metadata for a given user query.
* **Context-Aware SQL Generation**: Powered by GPT-4, constrained by retrieved schema context.
* **Security Guardrails**: Explicitly blocks non-DETERMINISTIC or destructive queries (`DELETE`, `DROP`, `UPDATE`).
* **Automatic Joins**: The grounding layer includes relationship mappings to help the LLM navigate foreign key constraints.

---

##  Accuracy & Hallucination Reduction

To ensure the system is production-ready and doesn't "invent" columns, SchemaSight implements a **Three-Tier Validation Layer**:

1. **Context Pinning (Grounding)**: Instead of providing the entire database schema in the prompt (which creates noise), we use a Vector DB to perform semantic search. If a user asks about "Revenue," the system retrieves the `order_items` and `unit_price` metadata, forcing the LLM to stay within those bounds.
2. **Strict SQL Sanitization**: A regex-based safety layer scans generated SQL for forbidden keywords. If the LLM attempts to generate a `DROP` or `ALTER` command, the execution is terminated before hitting the database.
3. **Schema Integrity Check**: The prompt template requires the LLM to use a "Chain of Thought" process to identify which retrieved tables are necessary for the JOIN before writing the final query.

---

##  Project Structure

```text
.
├── app.py              # Streamlit UI & Main Logic
├── db_setup.sql        # PostgreSQL Schema & Seed Data
├── embeddings.py       # FAISS indexing & metadata logic
├── requirements.txt    # Python dependencies
└── README.md           # Documentation

```

---

##  Getting Started

### 1. Database Setup

Ensure you have a PostgreSQL instance running. Execute the `db_setup.sql` file to create the `customers`, `products`, `orders`, and `order_items` tables.

### 2. Environment Variables

Create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/schemasight_db

```

### 3. Installation

```bash
pip install -r requirements.txt

```

### 4. Launch the Prototype

```bash
streamlit run app.py

```

---

##  Database Schema

The system is grounded in the following relational model:

| Table | Key Columns | Description |
| --- | --- | --- |
| **customers** | `id`, `name`, `city` | Stores user profiles. |
| **products** | `id`, `name`, `price` | Product inventory. |
| **orders** | `customer_id`, `status` | Connects users to transactions. |
| **order_items** | `order_id`, `product_id` | Line items for each order. |

