from .base import Agent
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
import json

class Receipts(BaseModel):
    receipts: list[str] = Field(description="The list of receipts names")

class RecipeMapping(BaseModel):
    id: int = Field(description="The id of the receipt")
    name: str = Field(description="The name of the receipt")

class RecipesMapping(BaseModel):
    recipes: list[RecipeMapping] = Field(description="The list of dictionaries of receipts and their ids")
    

class ReceiptFinder(Agent):
    def invoke(self):
        prompt = PromptTemplate.from_template(
            "Sei un cercatore di ricette"
            "Ti viene fornita un contesto e devi trovare le ricette dal contesto che rispondono alla query."
            "Leggi attentamente la domanda e il contesto!"
            "<domanda>\n{domanda}\n</domanda>\n\n"
            "<contesto>\n{contexts}\n</contesto>"
        )
        chain = prompt | self.model.with_structured_output(Receipts)

        recipes = chain.invoke({"contexts": self.state['contexts'], "domanda": self.state['domanda']})
        recipes_mapping = self._get_ids(recipes.receipts)

        if len(recipes_mapping.recipes) == 0:
            return {'receipts': [{'1' : 'Nessuna ricetta'}]}

        return {'receipts': [{item.id: item.name} for item in recipes_mapping.recipes]}
    
    def _get_ids(self, receipts: list[str]):
        with open('data/Misc/dish_mapping.json', 'r') as f:
            mapping = json.load(f)

        present = False
        recipes_list = []
        receipts = list(set(receipts))
        # Iterate through receipts and find matching ids from mapping
        for receipt in receipts:
            if receipt in mapping:
                recipes_list.append(RecipeMapping(id=mapping[receipt], name=receipt))
                present = True

        if not present:
            recipes_list.append(RecipeMapping(id=1, name="Nessuna ricetta"))
        
        return RecipesMapping(recipes=recipes_list)
    
        prompt = PromptTemplate.from_template(
            "Questa è la lista di ricette: {receipts}\n\n"
            "Il tuo compito è estrarre gli id delle ricette insieme al nome della ricetta, in base al mapping."
            "Se non trovi nessuna ricetta nel mapping, restituisci array vuoto!"
            "Se una ricetta non è presente nel mapping, escludila dalla lista!"
            "Non ripeti gli stessi id!"
            "Qui il mapping\n\n<mapping>\n{mapping}\n</mapping>"
        )

        chain = prompt | self.model.with_structured_output(RecipesMapping)

        return chain.invoke({"receipts": receipts, "mapping": mapping})
    

