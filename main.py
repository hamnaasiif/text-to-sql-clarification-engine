from app.services.schema_service import get_database_schema
from app.services.ambiguity_service import check_ambiguity
from app.services.conversation_service import ConversationState, resolve_option
from app.services.sql_generator import generate_sql, regenerate_sql_with_error
from app.services.query_executor import execute_query
from app.services.response_generator import generate_response


def run_pipeline(question: str):
    schema = get_database_schema()

    # Step 1: Ambiguity check
    ambiguity = check_ambiguity(question, schema)

    if ambiguity.is_ambiguous:
        state = ConversationState()
        state.start(question)

        print(f"\nThis question has {len(ambiguity.ambiguities)} thing(s) to clarify:\n")

        for dim in ambiguity.ambiguities:
            print(f"{dim.question}")
            for idx, opt in enumerate(dim.options, 1):
                print(f"  {idx}. {opt}")
            raw_answer = input("\nYour answer: ")
            resolved_answer = resolve_option(raw_answer, dim.options)
            state.add_resolution(dim.aspect, dim.question, resolved_answer)
            print()
        intent = state.get_resolved_intent()
    else:
        intent = question
    # Step 2: SQL generate karo
    sql_result, results = generate_and_execute_sql(intent, schema)
    print(f"\nFinal SQL used:\n{sql_result.sql_query}")

    # Step 4: Natural language answer
    final_answer = generate_response(intent, results)
    print(f"\nAnswer: {final_answer}")

def generate_and_execute_sql(intent: str, schema: dict, max_retries: int = 2):
    sql_result = generate_sql(intent, schema)

    for attempt in range(max_retries + 1):
        try:
            results = execute_query(sql_result.sql_query)
            return sql_result, results
        except Exception as e:
            if attempt == max_retries:
                raise  # sab retries khatam, ab error propagate hone do

            print(f"\nSQL failed (attempt {attempt + 1}): {e}")
            print("Retrying with corrected query...")
            sql_result = regenerate_sql_with_error(
                intent, schema, sql_result.sql_query, str(e)
            )

    return sql_result, results

if __name__ == "__main__":
    user_question = input("Ask a question about your data: ")
    run_pipeline(user_question)