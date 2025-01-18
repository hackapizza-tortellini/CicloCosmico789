import os
from pydantic import BaseModel, Field
from langchain_ibm import ChatWatsonx
from langchain.prompts import PromptTemplate
from src.database import Database

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

class RestaurantLicense(BaseModel):
    name: str = Field(default=..., description="The name of the restaurant without the word 'ristorante' or anything similar.")
    chef: str
    planet: str = Field(default=..., description="""The planet"where the restaurant is located, without the word 'pianeta' or anything similar.
Choose from Tatooine,Asgard,Namecc,Arrakis,Krypton,Pandora,Cybertron,Ego,Montressosr,Klyntar                        
""")
    licenses: list[License]

class RestaurantRecipe(BaseModel):
    name: str = Field(default=..., description="The name of the restaurant without the word 'ristorante' or anything similar.")
    recipes: list[Recipe]

db = Database()
db.create_tables()

for file in os.listdir("data/MenuTxtPdfMiner"):
    with open(f"data/MenuTxtPdfMiner/{file}", "r") as f:
        text = f.read()
        nome_ristorante = file.split(".")[0]
        intestazione = text.split("Menu")[0]
        menu = text.split("Menu")[1]

    llm = ChatWatsonx(
        model_id = 'mistralai/mistral-large',
        max_tokens=29000,
        project_id=os.getenv('WATSONX_PROJECT_ID'),
    )

    prompt_intestazione = PromptTemplate.from_template(
        "Extract the restaurant from the text, along with the chef and the licenses: {text}"
    )
    prompt_menu = PromptTemplate.from_template(
        "Extract the recipes from the text, along with the ingredients and the techniques: {text}"
    )

    chain_intestazione = prompt_intestazione | llm.with_structured_output(RestaurantLicense).with_retry(stop_after_attempt=3)
    chain_menu = prompt_menu | llm.with_structured_output(RestaurantRecipe).with_retry(stop_after_attempt=3)

    res_intestazione = chain_intestazione.invoke({"text": text})
    res_menu = chain_menu.invoke({"text": menu})

    res_intestazione.name = nome_ristorante
    res_menu.name = nome_ristorante

    # Add restaurant and get its reference
    ristorante = db.add_restaurant(res_intestazione.name, res_intestazione.chef, res_intestazione.planet, res_intestazione.model_dump()['licenses'])
    
    # Add ingredients and get their references
    ingredienti = db.add_ingredients(res_menu.model_dump()['ingredients'])
    
    all_techniques = []
    for recipe in res_menu.model_dump()['recipes']:
        all_techniques.extend(recipe['techniques'])
    all_techniques = list(set(all_techniques))  # Remove duplicates
    
    # Add techniques and get their references
    tecniche = db.add_techniques(all_techniques)
    
    # Add recipes and link them with ingredients and techniques
    db.add_recipes(ristorante, res_menu.model_dump()['recipes'], ingredienti, tecniche)

    print(res_intestazione)
    print(res_menu)
    break