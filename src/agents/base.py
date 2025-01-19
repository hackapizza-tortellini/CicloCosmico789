from langgraph.graph import StateGraph
from langchain_ibm import ChatWatsonx
import os

class Agent:
    def __init__(self, state: StateGraph, streaming: bool = True) -> None:
        self.state = state
        self.model = ChatWatsonx(
                model_id = 'mistralai/mistral-large',
                max_tokens=1000,
                project_id=os.getenv('WATSONX_PROJECT_ID'),
            )
        self.streaming = streaming