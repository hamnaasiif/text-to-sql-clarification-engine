from datetime import date
import json
from groq import Groq
from dotenv import load_dotenv
import os
from app.models.ambiguity import AmbiguityResult

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


AMBIGUITY_PROMPT = """Today's date is {today}.

You are analyzing a user's natural language question
that will be converted into a SQL query against this database schema:

{schema}

Determine if the question is AMBIGUOUS. A question can have MULTIPLE
separate ambiguous aspects at once (e.g. an undefined metric AND an
undefined time range). Identify EACH ambiguous aspect SEPARATELY —
do not combine them into one question.

IMPORTANT — only flag an ambiguity if it would change the actual DATA
returned (e.g. which rows are included, how results are aggregated,
what time period or threshold applies, which metric defines a vague
term like "best" or "most"). Do NOT flag ambiguity about which columns
to display, output formatting, or presentation — always include all
reasonably relevant columns automatically without asking.

Respond with ONLY valid JSON, no other text, in exactly this shape:
{{
  "is_ambiguous": true or false,
  "reason": "short explanation",
  "ambiguities": [
    {{
      "aspect": "short label like 'metric' or 'time_range'",
      "question": "a single clear clarification question for this aspect only",
      "options": ["option1", "option2", ...]
    }}
  ] or null if not ambiguous
}}

User question: {question}
"""


def check_ambiguity(question: str, schema: dict) -> AmbiguityResult:
    prompt = AMBIGUITY_PROMPT.format(
        today=date.today().isoformat(),
        schema=json.dumps(schema, indent=2),
        question=question
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.choices[0].message.content
    parsed_json = json.loads(raw_text)

    return AmbiguityResult(**parsed_json)


if __name__ == "__main__":
    from app.services.schema_service import get_database_schema

    schema = get_database_schema()
    result = check_ambiguity("who made the most purchases last year", schema)
    print(result)