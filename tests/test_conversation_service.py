import unittest
from app.services.conversation_service import resolve_option, ConversationState


class TestConversationService(unittest.TestCase):
    def setUp(self):
        self.options = [
            "Total quantity sold",
            "Total revenue generated",
            "Number of orders"
        ]

    def test_numeric_index_resolution(self):
        self.assertEqual(resolve_option("1", self.options), "Total quantity sold")
        self.assertEqual(resolve_option("2", self.options), "Total revenue generated")
        self.assertEqual(resolve_option("3", self.options), "Number of orders")

    def test_exact_text_resolution(self):
        self.assertEqual(resolve_option("Total quantity sold", self.options), "Total quantity sold")
        self.assertEqual(resolve_option("total revenue generated", self.options), "Total revenue generated")

    def test_partial_text_resolution(self):
        self.assertEqual(resolve_option("revenue", self.options), "Total revenue generated")
        self.assertEqual(resolve_option("quantity", self.options), "Total quantity sold")

    def test_fallback_unmatched(self):
        self.assertEqual(resolve_option("custom value", self.options), "custom value")

    def test_conversation_state_resolved_intent(self):
        state = ConversationState()
        state.start("What are top selling products?")
        resolved = resolve_option("1", self.options)
        state.add_resolution("metric", "Which metric?", resolved)
        intent = state.get_resolved_intent()
        self.assertIn("Total quantity sold", intent)


if __name__ == "__main__":
    unittest.main()
