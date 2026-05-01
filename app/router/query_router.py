from dataclasses import dataclass
from enum import Enum

class QueryType(str, Enum):
    LOOKUP = "lookup"
    AGGREGATION = "aggregation"
    UNKNOWN = "unknown"
    
@dataclass
class RouteDecision:
    query: str
    query_type: QueryType
    reason: str
    
class QueryRouter:
    """
    Decides whether a user query should be handled by:
    - vector search for lookup queries
    - DuckDB for aggregation queries
    """
    
    AGGREGATION_KEYWORDS = {
        "total",
        "sum",
        "final",
        "overall",
        "average",
        "avg",
        "count",
        "how many",
        "top",
        "highest",
        "lowest",
        "maximum",
        "minimum",
        "breakdown",
        "category",
        "categories",
        "month-wise",
        "monthly",
        "trend",
        "percentage",
        "percent",
        "group by",
    }
    
    @classmethod
    def route(cls, query: str) -> RouteDecision:
        if not query or not query.strip():
            return RouteDecision(
                query=query,
                query_type=QueryType.UNKNOWN,reason="Empty query."
            )
        normalized_query = query.lower()
        for keyword in cls.AGGREGATION_KEYWORDS:
            if keyword in normalized_query:
                return RouteDecision(
                    query=query,
                    query_type=QueryType.AGGREGATION,reason=f"Detected aggregation keyword: {keyword}"
                )
        return RouteDecision(
            query=query,
            query_type=QueryType.LOOKUP,
            reason="No aggregation keyword detected. Using vector lookup."
        )