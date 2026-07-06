from datetime import date
import json
from groq import Groq
from dotenv import load_dotenv
import os
from app.models.sql import SQLResult

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


SQL_PROMPT = """Today's date is {today}.. You are a PostgreSQL expert. Given a database schema and
a clear user intent, generate a single valid PostgreSQL SELECT query.

DATABASE SCHEMA:
{schema}

USER INTENT:
{intent}

RULES:
- Generate SELECT queries only. Never generate INSERT, UPDATE, DELETE, DROP, or ALTER.
- Use only tables and columns that exist in the schema above.
- Use proper JOINs when data spans multiple tables.
- When using ORDER BY with LIMIT, always add a secondary tie-breaker
  (e.g. the primary key column) to guarantee deterministic, repeatable
  results even when values are tied.

Respond with ONLY valid JSON, no other text, in exactly this shape:
{{
  "sql_query": "the SQL query as a single string",
  "explanation": "one sentence explaining what the query does"
}}
"""
SQL_FIX_PROMPT = """Today's date is {today}.

You previously generated this PostgreSQL query for the given schema
and user intent, but it failed when executed.

DATABASE SCHEMA:
{schema}

USER INTENT:
{intent}

FAILED SQL QUERY:
{failed_sql}

DATABASE ERROR:
{error_message}

Fix the query so it runs successfully against the schema above, while
still satisfying the original user intent. Only use tables/columns
that actually exist in the schema.

Respond with ONLY valid JSON, no other text, in exactly this shape:
{{
  "sql_query": "the corrected SQL query as a single string",
  "explanation": "one sentence explaining what was wrong and how you fixed it"
}}
"""


def regenerate_sql_with_error(intent: str, schema: dict, failed_sql: str, error_message: str) -> SQLResult:
    prompt = SQL_FIX_PROMPT.format(
        today=date.today().isoformat(),
        schema=json.dumps(schema, indent=2),
        intent=intent,
        failed_sql=failed_sql,
        error_message=error_message
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.choices[0].message.content
    parsed_json = json.loads(raw_text)

    return SQLResult(**parsed_json)

def generate_sql(intent: str, schema: dict) -> SQLResult:
    prompt = SQL_PROMPT.format(
        today=date.today().isoformat(),
        schema=json.dumps(schema, indent=2),
        intent=intent
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.choices[0].message.content
    parsed_json = json.loads(raw_text)

    return SQLResult(**parsed_json)


if __name__ == "__main__":
    from app.services.schema_service import get_database_schema

    schema = get_database_schema()
    intent = "Find the customer with the highest total amount spent across all completed orders"
    result = generate_sql(intent, schema)
    print("SQL:", result.sql_query)
    print("Explanation:", result.explanation)
    # Test error recovery — simulate a wrong column name
    bad_sql = "SELECT customer_name FROM customers;"
    fake_error = 'column "customer_name" does not exist'
    fixed = regenerate_sql_with_error(intent, schema, bad_sql, fake_error)
    print("\nFixed SQL:", fixed.sql_query)
    print("Explanation:", fixed.explanation)