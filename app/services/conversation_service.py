def resolve_option(user_input: str, options: list[str]) -> str:
    if not options:
        return user_input.strip()

    cleaned = user_input.strip()

    # 1. Numeric index check (1-based)
    if cleaned.isdigit():
        idx = int(cleaned)
        if 1 <= idx <= len(options):
            return options[idx - 1]

    # 2. Case-insensitive exact match
    cleaned_lower = cleaned.lower()
    for opt in options:
        if cleaned_lower == opt.strip().lower():
            return opt

    # 3. Partial substring match
    matches = [opt for opt in options if cleaned_lower in opt.lower()]
    if len(matches) == 1:
        return matches[0]

    # 4. Fallback if no match
    return cleaned


class ConversationState:
    def __init__(self):
        self.original_question = None
        self.resolutions = []  # list of (aspect, question, answer)

    def start(self, question: str):
        self.original_question = question
        self.resolutions = []

    def add_resolution(self, aspect: str, question: str, answer: str):
        self.resolutions.append((aspect, question, answer))

    def get_resolved_intent(self) -> str:
        clarifications = "; ".join(
            f"{q} -> {a}" for _, q, a in self.resolutions
        )
        return f"{self.original_question} (Clarifications: {clarifications})"


if __name__ == "__main__":
    opts = ["Total quantity sold", "Total revenue generated"]
    print("Test index 1:", resolve_option("1", opts))
    print("Test text match:", resolve_option("revenue", opts))