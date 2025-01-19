
from .base import Agent
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
import json
from langgraph.graph import StateGraph
from ..tools.file_finder import search_pdfs_with_filters

class Receipts(BaseModel):
    receipts: list[str] = Field(description="The list of receipts names")

class RecipeMapping(BaseModel):
    id: int = Field(description="The id of the receipt")
    name: str = Field(description="The name of the receipt")

class RecipesMapping(BaseModel):
    recipes: list[RecipeMapping] = Field(description="The list of dictionaries of receipts and their ids for example {1: 'pizza'}")
    

class ReceiptFinder(Agent):
    def invoke(self):
        prompt = PromptTemplate.from_template(
            "Sei un cercatore di ricette"
            "Ti viene fornita una lista di contesti e devi trovare le ricette che sono correlate alla query in base ai contesti."
            "<domanda>\n{domanda}\n</domanda>\n\n"
            "<contexts>\n{contexts}\n</contexts>"
        )
        chain = prompt | self.model.with_structured_output(Receipts)

        recipes = chain.invoke({"contexts": self.state['contexts'], "domanda": self.state['domanda']})
        recipes_mapping = self._get_ids(recipes.receipts)

        return {'receipts': [{item.id: item.name} for item in recipes_mapping.recipes]}
    
    def _get_ids(self, receipts: list[str]):
        with open('data/Misc/dish_mapping.json', 'r') as f:
            mapping = json.load(f)
        
        prompt = PromptTemplate.from_template(
            "Questa è la lista di ricette: {receipts}\n\n"
            "Il tuo compito è estrarre gli id delle ricette along with the name of the receipt"
            "Qui il mapping\n\n<mapping>\n{mapping}\n</mapping>"
        )

        chain = prompt | self.model.with_structured_output(RecipesMapping)

        return chain.invoke({"receipts": receipts, "mapping": mapping})
