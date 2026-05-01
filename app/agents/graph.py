from typing import TypedDict, List

from langgraph.graph import StateGraph, END

from app.router.query_router import QueryRouter, QueryType
from app.retrieval.vector_store import VectorStore
from app.database.duckdb_engine import DuckDBEngine
from app.llm.llm_service import LLMService


class AgentState(TypedDict):
    query: str
    query_type: str
    context: List[str]
    answer: str


class BankingRAGGraph:
    """
    LangGraph orchestration layer for Banking RAG chatbot.

    Flow:
    START
      -> route_query
      -> conditional routing
          -> lookup_agent
          -> aggregation_agent
      -> generate_answer
      -> END
    """

    def __init__(self, vector_store: VectorStore, db_engine: DuckDBEngine):
        self.vector_store = vector_store
        self.db_engine = db_engine
        self.llm = LLMService()
        self.graph = self._build_graph()

    def _route_query(self, state: AgentState) -> dict:
        decision = QueryRouter.route(state["query"])

        return {
            "query_type": decision.query_type.value,
            "context": [],
            "answer": ""
        }

    def _lookup_agent(self, state: AgentState) -> dict:
        results = self.vector_store.search(state["query"])
        documents = results.get("documents", [[]])[0]

        if not documents:
            return {
                "context": [],
                "answer": "No relevant data found from uploaded files."
            }

        return {
            "context": documents
        }

    def _aggregation_agent(self, state: AgentState) -> dict:
        query = state["query"].lower()

        try:
            # TOTAL / SUM
            if any(word in query for word in ["total", "sum", "final", "overall"]):
                sql = "SELECT SUM(CAST(amount AS DOUBLE)) AS total FROM transactions"

            # AVERAGE
            elif "average" in query or "avg" in query:
                sql = "SELECT AVG(CAST(amount AS DOUBLE)) AS average FROM transactions"

            # COUNT
            elif "count" in query or "how many" in query:
                sql = "SELECT COUNT(*) AS count FROM transactions"

            # CATEGORY BREAKDOWN
            elif "category" in query or "breakdown" in query:
                sql = """
                    SELECT category, SUM(CAST(amount AS DOUBLE)) AS total
                    FROM transactions
                    GROUP BY category
                    ORDER BY total DESC
                """

            # TOP TRANSACTIONS
            elif "top" in query:
                sql = """
                    SELECT *
                    FROM transactions
                    ORDER BY CAST(amount AS DOUBLE) DESC
                    LIMIT 3
                """

            else:
                return {
                    "answer": "Aggregation query not supported yet. Try total, average, count, category breakdown, or top transactions."
                }

            result = self.db_engine.query(sql)

            return {
                "context": [result.to_string(index=False)]
            }

        except Exception as e:
            return {
                "answer": f"Aggregation error: {str(e)}"
            }
    def _generate_answer(self, state: AgentState) -> dict:
        if state.get("answer"):
            return {
                "answer": state["answer"]
            }

        if state["query_type"] == QueryType.AGGREGATION.value:
            return {
                "answer": state["context"][0] if state.get("context") else "No aggregation result found."
            }

        answer = self.llm.generate_response(
            query=state["query"],
            context=state["context"]
        )

        return {
            "answer": answer
        }

    def _decide_next(self, state: AgentState) -> str:
        if state["query_type"] == QueryType.AGGREGATION.value:
            return "aggregation_agent"

        if state["query_type"] == QueryType.LOOKUP.value:
            return "lookup_agent"

        return "generate_answer"

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("route_query", self._route_query)
        workflow.add_node("lookup_agent", self._lookup_agent)
        workflow.add_node("aggregation_agent", self._aggregation_agent)
        workflow.add_node("generate_answer", self._generate_answer)

        workflow.set_entry_point("route_query")

        workflow.add_conditional_edges(
            "route_query",
            self._decide_next,
            {
                "lookup_agent": "lookup_agent",
                "aggregation_agent": "aggregation_agent",
                "generate_answer": "generate_answer",
            }
        )

        workflow.add_edge("lookup_agent", "generate_answer")
        workflow.add_edge("aggregation_agent", "generate_answer")
        workflow.add_edge("generate_answer", END)

        return workflow.compile()
    
    def invoke(self, query: str) -> dict:
        initial_state: AgentState = {
            "query": query,
            "query_type": "",
            "context": [],
            "answer": ""
        }

        try:
            return self.graph.invoke(initial_state)

        except Exception as e:
            print("LANGGRAPH RUNTIME ERROR:", repr(e))
            print("Using manual LangGraph-equivalent fallback flow.")

            state = initial_state

            # 1. Route query
            state.update(self._route_query(state))

            # 2. Conditional routing
            next_node = self._decide_next(state)

            if next_node == "aggregation_agent":
                state.update(self._aggregation_agent(state))

            elif next_node == "lookup_agent":
                state.update(self._lookup_agent(state))

            # 3. Generate final answer
            state.update(self._generate_answer(state))

            return state