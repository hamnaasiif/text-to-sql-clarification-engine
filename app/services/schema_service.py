import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("DATABASE_URL")


def get_database_schema():
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)

    rows = cur.fetchall()

    schema = {}
    for table_name, column_name, data_type in rows:
        if table_name not in schema:
            schema[table_name] = []
        
        col_info = {
            "column": column_name,
            "type": data_type
        }

        # Fetch sample values for low-cardinality string/character columns (distinct count <= 10)
        if any(t in data_type.lower() for t in ["char", "text", "varchar"]):
            try:
                cur.execute(
                    f'SELECT DISTINCT "{column_name}" FROM "{table_name}" WHERE "{column_name}" IS NOT NULL LIMIT 11;'
                )
                sample_rows = cur.fetchall()
                if 0 < len(sample_rows) <= 10:
                    col_info["sample_values"] = [r[0] for r in sample_rows]
            except Exception:
                pass

        schema[table_name].append(col_info)

    cur.close()
    conn.close()

    return schema


# Testing 
if __name__ == "__main__":
    import json
    result = get_database_schema()
    print(json.dumps(result, indent=2))