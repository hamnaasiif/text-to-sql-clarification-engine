from app.services.sql_generator import generate_sql
from app.services.query_executor import execute_query


def run_baseline(question: str, schema: dict):
    sql_result = generate_sql(question, schema)  # raw question, no clarification
    try:
        results = execute_query(sql_result.sql_query)
    except Exception as e:
        results = f"ERROR: {e}"
    return sql_result.sql_query, results


def test_consistency(question: str, schema: dict, runs: int = 5):
    print(f"\nRunning '{question}' {runs} times...\n")
    for i in range(runs):
        sql, results = run_baseline(question, schema)
        # SQL ka pehla result dikhate hain (kaunsa customer/metric chuna)
        print(f"Run {i+1}: {results}")


if __name__ == "__main__":
    from app.services.schema_service import get_database_schema
    schema = get_database_schema()

    test_consistency("What are our top selling products?", schema, runs=3)