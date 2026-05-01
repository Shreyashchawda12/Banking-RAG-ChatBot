from app.router.query_router import QueryRouter, QueryType


def test_lookup_query():
    decision = QueryRouter.route("What is home loan interest rate?")

    assert decision.query_type == QueryType.LOOKUP


def test_total_query_is_aggregation():
    decision = QueryRouter.route("What is the total transaction amount?")

    assert decision.query_type == QueryType.AGGREGATION


def test_average_query_is_aggregation():
    decision = QueryRouter.route("What is my average monthly spending?")

    assert decision.query_type == QueryType.AGGREGATION


def test_top_query_is_aggregation():
    decision = QueryRouter.route("Show top 3 spending categories")

    assert decision.query_type == QueryType.AGGREGATION


def test_empty_query_is_unknown():
    decision = QueryRouter.route("")

    assert decision.query_type == QueryType.UNKNOWN