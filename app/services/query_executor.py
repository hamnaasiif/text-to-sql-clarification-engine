import psycopg2
from dotenv import load_dotenv
import os
from app.services.sql_validator import is_safe_sql

load_dotenv()
db_url = os.getenv("DATABASE_URL")


def execute_query(sql_query: str):
    safe, reason = is_safe_sql(sql_query)
    if not safe:
        raise ValueError(f"Query rejected: {reason}")

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute(sql_query)
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    cur.close()
    conn.close()

    results = [dict(zip(columns, row)) for row in rows]
    return results


if __name__ == "__main__":
    query = """
        SELECT c.name, SUM(o.total_amount) AS total_spent
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.order_status = 'completed'
        GROUP BY c.name
        ORDER BY total_spent DESC
        LIMIT 1;
    """
    result = execute_query(query)
    print(result)