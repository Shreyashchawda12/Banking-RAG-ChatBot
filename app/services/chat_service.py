from app.router.query_router import QueryRouter, QueryType
from app.retrieval.vector_store import VectorStore
from app.database.duckdb_engine import DuckDBEngine
from app.llm.llm_service import LLMService


class ChatService:
    """
    Main service that handles user queries.
    """

    def __init__(self, vector_store: VectorStore, db_engine: DuckDBEngine):
        self.vector_store = vector_store
        self.db_engine = db_engine
        self.llm = LLMService()

    def handle_query(self, query: str) -> str:
        decision = QueryRouter.route(query)

        if decision.query_type == QueryType.LOOKUP:
            return self._handle_lookup(query)

        elif decision.query_type == QueryType.AGGREGATION:
            return self._handle_aggregation(query)

        else:
            return "Please provide a valid query."

    def _handle_lookup(self, query: str) -> str:
        results = self.vector_store.search(query)

        documents = results.get("documents", [[]])[0]

        if not documents:
            return "No relevant data found."

        return self.llm.generate_response(query, documents)

    def _handle_aggregation(self, query: str) -> str:

        if "total" in query.lower():
            sql = "SELECT SUM(amount) AS total FROM transactions"
        else:
            return "Aggregation query not supported yet."

        result = self.db_engine.query(sql)

        context = [result.to_string(index=False)]

        return self.llm.generate_response(query, context)