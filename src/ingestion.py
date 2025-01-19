from pydantic import BaseModel, Field
import os
import json
from langchain_core.prompts import PromptTemplate
from langchain_ibm import ChatWatsonx

class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    techniques: list[str]

class License(BaseModel):
    name: str = Field(default=..., description="The name of the license, without the word 'licenza' or anything similar. Use the following acronyms : P, G, e+, Mx, LTK")
    acronym: str = Field(default=..., description=f"""The acronym of the license 
Psionica: P
Gravitazione: G
Antimateria: e+
Magnetica: Mx
Livello/Grado Sviluppo Tecnologico: LTK
Temporale: t
Quantica: Q
Luce: c
""")
    level: str = Field(default=..., description="The level of the license, without the word 'livello' or anything similar.")

class Restaurant(BaseModel):
    name: str = Field(default=..., description="The name of the restaurant without the word 'ristorante' or anything similar.")
    chef: str
    planet: str = Field(default=..., description="""The planet"where the restaurant is located, without the word 'pianeta' or anything similar.
Choose from Tatooine,Asgard,Namecc,Arrakis,Krypton,Pandora,Cybertron,Ego,Montressosr,Klyntar                        
""")
    licenses: list[License]
    recipes: list[Recipe]

# class RestaurantRecipe(BaseModel):
#     name: str = Field(default=..., description="The name of the restaurant without the word 'ristorante' or anything similar.")
#     recipes: list[Recipe]

# todo: add order of the chef
for file in os.listdir('data/MenuTxtPdfMiner'):
    if file.split('.')[0]+'.json' != 'Universo Gastronomico di Namecc.json':
        continue
    with open(f'data/MenuTxtPdfMiner/{file}', 'r') as f:
        text = f.read()
    
    llm = ChatWatsonx(
        model_id = 'mistralai/mistral-large',
        max_tokens=20000,
        project_id=os.getenv('WATSONX_PROJECT_ID'),
    )

    prompt_intestazione = PromptTemplate.from_template(
        "Extract the restaurant from the text, along with the chef and the licenses: {text}"
    )

    chain = prompt_intestazione | llm.with_structured_output(Restaurant)

    restaurant = chain.invoke({"text": text})
    # Save restaurant data to JSON
    restaurant_data = restaurant.model_dump()
    json_filename = f"data/MenuJSON/{file.split('.')[0]}.json"
    
    
    with open(json_filename, "w") as f:
        json.dump(restaurant_data, f, indent=2)
