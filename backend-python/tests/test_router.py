
import pytest
from app.services import AIService

class TestRouter:
    """
    Tests the Routing inputs (Cluster A vs Cluster B equivalent).
    Currently implemented via Regex, but tests define the Contract.
    """
    
    def test_cluster_a_sql_intents(self):
        """Test Cluster A: SQL/Count/List intents"""
        sql_queries = [
            "How many invoices are there?",
            "List all files",
            "Zeige alle Dokumente",
            "Count contracts"
        ]
        for q in sql_queries:
            plan = AIService.plan_query(q)
            assert plan["intent"] == "SQL", f"Query '{q}' should be routed to SQL (Cluster A)"

    def test_cluster_b_search_intents(self):
        """Test Cluster B: Semantic Search intents"""
        search_queries = [
            "What is the address of TechCorp?",
            "Wer ist Max Mustermann?",
            "Details about the project"
        ]
        for q in search_queries:
            plan = AIService.plan_query(q)
            assert plan["intent"] == "SEARCH", f"Query '{q}' should be routed to SEARCH (Cluster B)"

    def test_sql_injection_safety(self):
        """Test that suspicious SQL patterns don't crash the planner"""
        # Note: The planner is just a router. If it routes to SQL, the Executor handles safety.
        # But we want to ensure it doesn't error out here.
        queries = [
            "List items; DROP TABLE users;",
            "Select * from users --",
            "Show me everything ' OR '1'='1"
        ]
        for q in queries:
            try:
                plan = AIService.plan_query(q)
                assert plan["intent"] in ["SQL", "SEARCH"]
            except Exception as e:
                pytest.fail(f"Planner crashed on injection attempt: {e}")

    def test_ambiguous_queries(self):
        """Test queries that could be both (Overlap)"""
        # "List documents about AI" -> Has "List" (SQL) AND "AI" (Semantic)
        # Our current logic prefers SQL (Regex Shortcut).
        q = "List documents about AI"
        plan = AIService.plan_query(q)
        assert plan["intent"] == "SQL" # Prefer structured list over semantic search for "List" keyword

