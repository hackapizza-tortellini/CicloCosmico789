from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

# Many-to-many relationship tables
ricetta_ingrediente = Table(
    'ricetta_ingrediente',
    Base.metadata,
    Column('ricetta_id', Integer, ForeignKey('ricetta.id')),
    Column('ingrediente_id', Integer, ForeignKey('ingrediente.id'))
)

ricetta_tecnica = Table(
    'ricetta_tecnica',
    Base.metadata,
    Column('ricetta_id', Integer, ForeignKey('ricetta.id')),
    Column('tecnica_id', Integer, ForeignKey('tecnica.id'))
)

class Ristorante(Base):
    __tablename__ = 'ristorante'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    chef = Column(String)
    planet = Column(String)
    
    # Relationships
    licenze = relationship("Licenza", back_populates="ristorante")

class Licenza(Base):
    __tablename__ = 'licenza'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    acronimo = Column(String)
    livello = Column(String)
    ristorante_id = Column(Integer, ForeignKey('ristorante.id'))
    
    # Relationships
    ristorante = relationship("Ristorante", back_populates="licenze")

class Ricetta(Base):
    __tablename__ = 'ricetta'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    ristorante_id = Column(Integer, ForeignKey('ristorante.id'))
    # Many-to-many relationships
    ingredienti = relationship("Ingrediente", secondary=ricetta_ingrediente)
    tecniche = relationship("Tecnica", secondary=ricetta_tecnica)

class Ingrediente(Base):
    __tablename__ = 'ingrediente'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String)

class Tecnica(Base):
    __tablename__ = 'tecnica'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String)

class Database:
    def __init__(self, db_url="sqlite:///db/database.db"):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(self.engine)
    
    def add_default_licenses(self, ristorante):
        """Add default licenses to a restaurant"""
        session = self.Session()
        default_licenses = [
            {"nome": "Psionica", "acronimo": "P", "livello": "0"},
            {"nome": "Gravitazione", "acronimo": "G", "livello": "0"},
            {"nome": "Antimateria", "acronimo": "e+", "livello": "0"},
            {"nome": "Magnetica", "acronimo": "Mx", "livello": "0"},
            {"nome": "Livello/Grado Sviluppo Tecnologico", "acronimo": "LTK", "livello": "1"},
        ]
        
        for license_data in default_licenses:
            license = Licenza(
                nome=license_data["nome"],
                acronimo=license_data["acronimo"],
                livello=license_data["livello"],
                ristorante=ristorante
            )
            session.add(license)
        
        session.commit()
        session.close()

    def add_restaurant(self, restaurant: str, chef: str, planet: str, licenze: list[dict[str, str]]):
        session = self.Session()
        ristorante = Ristorante(
            nome=restaurant,
            chef=chef,
            planet=planet
        )
        session.add(ristorante)
        session.flush()  # This ensures we get the ID
        self.add_default_licenses(ristorante)
        self.add_licenze(ristorante, licenze)
        session.commit()
        session.close()
        return ristorante

    def add_licenze(self, ristorante: Ristorante, licenze: list):
        session = self.Session()
        for licenza in licenze:
            licenza_esistente = session.query(Licenza).filter(Licenza.acronimo == licenza["acronimo"], Licenza.ristorante_id == ristorante.id).first()
            if licenza_esistente:
                 licenza_esistente.livello = licenza["livello"]
            else:
                licenza = Licenza(
                    nome=licenza["nome"],
                    acronimo=licenza["acronimo"],
                    livello=licenza["livello"],
                    ristorante=ristorante
                )
                session.add(licenza)
        session.commit()
        session.close()

    def add_recipes(self, ristorante: Ristorante, recipes: list, ingredienti: list[Ingrediente], tecniche: list[Tecnica]):
        session = self.Session()
        added_recipes = []
        for recipe_data in recipes:
            recipe = Ricetta(
                nome=recipe_data["name"],
                ristorante_id=ristorante.id
            )
            # Add ingredients to the recipe
            for ingredient_name in recipe_data["ingredients"]:
                # Find the corresponding ingredient object
                ingredient = next((ing for ing in ingredienti if ing.nome == ingredient_name), None)
                if ingredient:
                    recipe.ingredienti.append(ingredient)
            
            # Add techniques to the recipe
            for technique_name in recipe_data["techniques"]:
                # Find the corresponding technique object
                technique = next((tec for tec in tecniche if tec.nome == technique_name), None)
                if technique:
                    recipe.tecniche.append(technique)
            
            session.add(recipe)
            added_recipes.append(recipe)
        
        session.commit()
        session.close()
        return added_recipes

    def add_ingredients(self, ingredients: list[str]):
        session = self.Session()
        added_ingredients = []
        for ingredient_name in ingredients:
            # Check if ingredient already exists
            existing_ingredient = session.query(Ingrediente).filter_by(nome=ingredient_name).first()
            if existing_ingredient:
                added_ingredients.append(existing_ingredient)
                continue
                
            ingredient = Ingrediente(
                nome=ingredient_name
            )
            session.add(ingredient)
            session.flush()  # This ensures we get the ID
            added_ingredients.append(ingredient)
            
        session.commit()
        session.close()
        return added_ingredients

    def add_techniques(self, techniques: list[str]):
        session = self.Session()
        added_techniques = []
        for technique_name in techniques:
            # Check if technique already exists
            existing_technique = session.query(Tecnica).filter_by(nome=technique_name).first()
            if existing_technique:
                added_techniques.append(existing_technique)
                continue
                
            technique = Tecnica(
                nome=technique_name
            )
            session.add(technique)
            session.flush()  # This ensures we get the ID
            added_techniques.append(technique)
            
        session.commit()
        session.close()
        return added_techniques
    