from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class State(TypedDict):
    ingredients_or_techniques: list[str]
    chefs: list[str]
    planets: list[str]
    domanda: str
    query_restaurants: list[str]

    ristoranti: list[str] # the ristoranti that have the keywords
    receipts: list[dict[int, str]] # list of receipts and their ids [['receipt', 1], ['receipt', 2]]
    contexts: list[str] # list of contexts that have the keywords
