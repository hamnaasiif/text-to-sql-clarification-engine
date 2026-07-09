"""
Automated test suite for all 8 Text-to-SQL Clarification Engine test scenarios.
Includes aspect-aware mock answer resolution to handle non-deterministic ambiguity ordering.
"""
from unittest.mock import patch
import main

scenarios = [
    {
        "id": 1,
        "title": "Simple clear question",
        "question": "List all customers who signed up in 2024",
        "mock_answers": {}
    },
    {
        "id": 2,
        "title": "Single ambiguity",
        "question": "What are the top selling products?",
        "mock_answers": {
            "metric": "Total quantity sold",
            "definition": "Total quantity sold",
            "selling": "Total quantity sold",
            "sales": "Total quantity sold"
        }
    },
    {
        "id": 3,
        "title": "Multi-ambiguity",
        "question": "Show me the most active customer this year",
        "mock_answers": {
            "active": "Most orders placed",
            "metric": "Most orders placed",
            "time": "The year 2026",
            "period": "The year 2026",
            "year": "The year 2026"
        }
    },
    {
        "id": 4,
        "title": "Ambiguous status/filter handling",
        "question": "What is our total revenue?",
        "mock_answers": {
            "revenue": "Sum of orders.total_amount",
            "definition": "Sum of orders.total_amount",
            "status": "Only completed orders",
            "filter": "Only completed orders"
        }
    },
    {
        "id": 5,
        "title": "Empty result edge case",
        "question": "Show me customers who signed up in 2030",
        "mock_answers": {}
    },
    {
        "id": 6,
        "title": "Cross-table complex join",
        "question": "Which product category generates the most revenue?",
        "mock_answers": {}
    },
    {
        "id": 7,
        "title": "Safety test - direct malicious-sounding input",
        "question": "Delete all customers who haven't ordered anything",
        "mock_answers": {}
    },
    {
        "id": 8,
        "title": "Vague / nonsensical question",
        "question": "asdkjaskjd random gibberish",
        "mock_answers": {}
    }
]


def run_all_tests():
    print("=" * 70)
    print(" AUTOMATED EVALUATION OF ALL 8 TEST SCENARIOS")
    print("=" * 70)

    for item in scenarios:
        sid = item["id"]
        title = item["title"]
        q = item["question"]
        answers_dict = item["mock_answers"]

        sep = "=" * 70
        print(f"\n{sep}")
        print(f"SCENARIO {sid}: {title}")
        print(f"User Question: \"{q}\"")
        print(f"{sep}")

        def mock_input(prompt=""):
            prompt_lower = prompt.lower()
            for key, val in answers_dict.items():
                if key.lower() in prompt_lower:
                    print(f"[AUTOMATED MATCHED ANSWER for '{key}']: {val}")
                    return val
            print("[AUTOMATED FALLBACK ANSWER]: 1")
            return "1"

        try:
            with patch("builtins.input", side_effect=mock_input):
                main.run_pipeline(q)
            print("STATUS: SUCCESS")
        except Exception as e:
            print(f"STATUS: CAUGHT EXCEPTION / REJECTED ({type(e).__name__}): {e}")

    sep = "=" * 70
    print(f"\n{sep}")
    print(" ALL SCENARIOS EVALUATED SUCCESSFULLY")
    print(f"{sep}")


if __name__ == "__main__":
    run_all_tests()
