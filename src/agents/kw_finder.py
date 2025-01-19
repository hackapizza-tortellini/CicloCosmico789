
from .base import Agent
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import Optional

class Keywords(BaseModel):
    ingredients_or_techniques: Optional[list[str]] = Field(description="Le tecniche o gli ingredienti inclusi nei piatti da trovare")
    chefs: Optional[list[str]] = Field(description="Gli chef citati nella domanda")
    planets: Optional[list[str]] = Field(description="I pianeti citati nella domanda")
    query_restaurants: Optional[list[str]] = Field(description="I ristoranti citati nella domanda")

class KeywordsFinder(Agent):

    def invoke(self, query: str):

        prompt = PromptTemplate.from_template(
            "Questa è la domanda dell'utente: {query}\n\n"
            "Il tuo compito è estrarre ingredienti o tecniche o chef o pianeti o ristoranti citati nella domanda"
            "Se disponibili."
            "Per quanto riguarda gli ingredienti o le tecniche, devi estrarre solo quelli che sono devono essere presenti nei piatti da trovare."
            "Escludi gli ingredienti o le tecniche che non devono essere presenti nei piatti da trovare."
            "Se la domanda é 'quali piatti sono a base di pizza ma senza il pomodoro?' devi estrarre solo 'pizza'"
            "Se gli ingredienti o le tecniche contengono più parole, prendi solo le parole più significative."
            "Esempio: se l'ingrediente è 'Sashimi di Magikarp' prendi solo 'Sashimi'"
        )

        chain = prompt | self.model.with_structured_output(Keywords)

        result = chain.invoke({'query': query})

        return {
            'query_restaurants': result.query_restaurants,
            'ingredients_or_techniques': result.ingredients_or_techniques,
            'chefs': result.chefs,
            'planets': result.planets
        }
