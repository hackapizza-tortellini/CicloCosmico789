from langgraph.graph import StateGraph, START, END
from .state import State
from .agents.kw_finder import KeywordsFinder
from .agents.menu_finder import ReceiptFinder
from .tools.file_finder import search_pdfs_in_folder, search_pdfs_with_filters


def build_graph():
    graph_builder = StateGraph(State)

    graph_builder.add_node(
        'keywords_finder', 
        lambda state: KeywordsFinder(state).invoke(
            state['domanda']
        )
    )

    graph_builder.add_node(
        'menu_finder', 
        lambda state: search_pdfs_with_filters(state)
    )

    graph_builder.add_node(
        'receipt_finder', 
        lambda state: ReceiptFinder(state).invoke()
    )


    graph_builder.add_edge(START, 'keywords_finder')
    graph_builder.add_edge('keywords_finder', 'menu_finder')
    graph_builder.add_edge('menu_finder', 'receipt_finder')
    graph_builder.add_edge('receipt_finder', END)

    return graph_builder.compile()
