import sqlglot
from sqlglot.expressions import Select


def is_safe_sql(sql_query: str) -> tuple[bool, str]:
    try:
        parsed = sqlglot.parse_one(sql_query, dialect="postgres")
    except Exception as e:
        return False, f"Could not parse SQL: {e}"

    if not isinstance(parsed, Select):
        return False, "Only SELECT statements are allowed."

    return True, "Query is safe."


if __name__ == "__main__":
    test_queries = [
        "SELECT * FROM customers;",
        "DROP TABLE customers;",
        "DELETE FROM orders;",
        "SELECT name FROM customers WHERE customer_id = 1;",
    ]

    for q in test_queries:
        safe, reason = is_safe_sql(q)
        print(f"{q[:40]:40} -> Safe: {safe} | {reason}")