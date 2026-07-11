from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.schema_service import get_database_schema
from app.services.ambiguity_service import check_ambiguity
from app.services.session_service import create_session, get_session, add_resolution
from app.services.sql_generator import generate_sql
from app.services.query_executor import execute_query
from app.services.response_generator import generate_response
from app.services.sql_generator import regenerate_sql_with_error
from app.services.dataset_summary_service import get_dataset_summary

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        # TODO: add production frontend URL here (e.g. "https://your-app.vercel.app")
    ],  
    allow_methods=["*"],
    allow_headers=["*"],
)
class QuestionRequest(BaseModel):
    question: str


class AnswerRequest(BaseModel):
    session_id: str
    answer: str


def build_resolved_intent(session: dict) -> str:
    parts = [session["original_question"]]
    for r in session["resolutions"]:
        parts.append(f"{r['question']} -> {r['answer']}")
    return " (Clarifications: " + "; ".join(parts[1:]) + ")" if len(parts) > 1 else parts[0]


def generate_and_execute_sql(intent: str, schema: dict, max_retries: int = 2):
    sql_result = generate_sql(intent, schema)
    for attempt in range(max_retries + 1):
        try:
            results = execute_query(sql_result.sql_query)
            return sql_result, results
        except Exception as e:
            if attempt == max_retries:
                raise
            sql_result = regenerate_sql_with_error(intent, schema, sql_result.sql_query, str(e))
    return sql_result, results


def finalize(question: str, intent: str, schema: dict):
    sql_result, results = generate_and_execute_sql(intent, schema)
    answer = generate_response(intent, results)
    return {
        "status": "answered",
        "sql": sql_result.sql_query,
        "answer": answer
    }

@app.get("/dataset-summary")
def dataset_summary():
    return get_dataset_summary()
    
@app.post("/ask")
def ask(request: QuestionRequest):
    schema = get_database_schema()
    ambiguity = check_ambiguity(request.question, schema)

    if not ambiguity.is_ambiguous:
        return finalize(request.question, request.question, schema)

    ambiguities_data = [a.model_dump() for a in ambiguity.ambiguities]
    session_id = create_session(request.question, ambiguities_data)

    first = ambiguities_data[0]
    return {
        "status": "clarification_needed",
        "session_id": session_id,
        "aspect": first["aspect"],
        "question": first["question"],
        "options": first["options"]
    }


@app.post("/answer")
def answer(request: AnswerRequest):
    session = get_session(request.session_id)
    if session is None:
        return {"status": "error", "message": "Session not found"}

    current = session["ambiguities"][session["current_index"]]
    add_resolution(request.session_id, current["aspect"], current["question"], request.answer)

    session = get_session(request.session_id)  # refresh after update

    if session["current_index"] < len(session["ambiguities"]):
        next_dim = session["ambiguities"][session["current_index"]]
        return {
            "status": "clarification_needed",
            "session_id": request.session_id,
            "aspect": next_dim["aspect"],
            "question": next_dim["question"],
            "options": next_dim["options"]
        }

    schema = get_database_schema()
    intent = build_resolved_intent(session)
    return finalize(session["original_question"], intent, schema)


@app.get("/dataset-summary")
def dataset_summary():
    return get_dataset_summary()