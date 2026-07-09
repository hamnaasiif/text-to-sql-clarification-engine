from unittest.mock import patch
from app.services.schema_service import get_database_schema
from app.models.sql import SQLResult
import main

schema = get_database_schema()

# Jaan-boojh kar ek galat SQL query — non-existent column
fake_bad_sql = SQLResult(
    sql_query="SELECT customer_name FROM customers;",
    explanation="Intentionally broken for testing error recovery"
)

# generate_sql ko temporarily fake result dene ke liye "patch" kar rahe hain
with patch("main.generate_sql", return_value=fake_bad_sql):
    sql_result, results = main.generate_and_execute_sql(
        "Find the name of the customer who has spent the most money",
        schema
    )

print("\nFinal SQL that worked:", sql_result.sql_query)
print("Results:", results)
