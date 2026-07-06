from pydantic import BaseModel


class SQLResult(BaseModel):
    sql_query: str
    explanation: str