import json
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


RESPONSE_PROMPT = """The user asked: "{question}"

The database returned this data:
{results}

Write a short, natural language answer (1-2 sentences) that directly
answers the question using this data. Do not mention SQL or databases.
"""


def generate_response(question: str, results: list) -> str:
    prompt = RESPONSE_PROMPT.format(
        question=question,
        results=json.dumps(results, indent=2, default=str)
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    question = "Who is our best customer by total spending?"
    results = [{"name": "Ahmed Khan", "total_spent": "1300.00"}]

    answer = generate_response(question, results)
    print(answer)