from pydantic import BaseModel
from typing import Optional


class AmbiguityDimension(BaseModel):
    aspect: str  # e.g. "metric" or "time_range"
    question: str
    options: list[str]


class AmbiguityResult(BaseModel):
    is_ambiguous: bool
    reason: str
    ambiguities: Optional[list[AmbiguityDimension]] = None