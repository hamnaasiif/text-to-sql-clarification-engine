import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv
import os

load_dotenv()
db_url = os.getenv("DATABASE_URL")


def create_session(question: str, ambiguities: list) -> str:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO conversation_sessions (original_question, ambiguities)
        VALUES (%s, %s)
        RETURNING session_id
        """,
        (question, Json(ambiguities))
    )
    session_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return str(session_id)


def get_session(session_id: str) -> dict:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT original_question, ambiguities, current_index, resolutions
        FROM conversation_sessions
        WHERE session_id = %s
        """,
        (session_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        return None

    return {
        "original_question": row[0],
        "ambiguities": row[1],
        "current_index": row[2],
        "resolutions": row[3],
    }


def add_resolution(session_id: str, aspect: str, question: str, answer: str):
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute(
        "SELECT resolutions, current_index FROM conversation_sessions WHERE session_id = %s",
        (session_id,)
    )
    resolutions, current_index = cur.fetchone()
    resolutions.append({"aspect": aspect, "question": question, "answer": answer})

    cur.execute(
        """
        UPDATE conversation_sessions
        SET resolutions = %s, current_index = %s
        WHERE session_id = %s
        """,
        (Json(resolutions), current_index + 1, session_id)
    )
    conn.commit()
    cur.close()
    conn.close()
if __name__ == "__main__":
    fake_ambiguities = [
        {"aspect": "metric", "question": "Which metric?", "options": ["Revenue", "Order count"]}
    ]

    sid = create_session("Show me the best customer", fake_ambiguities)
    print("Created session:", sid)

    session = get_session(sid)
    print("Fetched session:", session)

    add_resolution(sid, "metric", "Which metric?", "Revenue")
    updated = get_session(sid)
    print("After resolution:", updated)