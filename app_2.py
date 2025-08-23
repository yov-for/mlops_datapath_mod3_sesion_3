from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select


# Configurar la base de datos
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
metadata = MetaData()

# Cargar la tabla existente
items = Table("items", metadata, autoload_with=engine)

# Configurar la sesión de SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Definir los modelos Pydantic
class Item(BaseModel):
    id: int
    name: str
    description: str = None

    class Config:
        from_attributes = True

class ItemCreate(BaseModel):
    name: str
    description: str = None

class ItemUpdate(ItemCreate):
    pass

# Inicializar la aplicación FastAPI
app = FastAPI()

# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}

# Operaciones CRUD

# Leer un elemento específico de la tabla
@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    with SessionLocal() as session:
        query = select(items).where(items.c.id == item_id)
        db_item = session.execute(query).fetchone()
        if db_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        return db_item._mapping

# Crear un nuevo elemento en la tabla
@app.post("/items/", response_model=Item)
def create_item(item: ItemCreate):
    with SessionLocal() as session:
        new_item = items.insert().values(name=item.name, description=item.description)
        result = session.execute(new_item)
        session.commit()
        created_item_id = result.inserted_primary_key[0]
        created_item = session.execute(select(items).where(items.c.id == created_item_id)).fetchone()
        return created_item._mapping

# Actualizar un elemento existente en la tabla
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemUpdate):
    with SessionLocal() as session:
        update_values = {k: v for k, v in item.dict().items() if v is not None}
        updated_item = items.update().where(items.c.id == item_id).values(**update_values)
        session.execute(updated_item)
        session.commit()
        updated_item = session.execute(select(items).where(items.c.id == item_id)).fetchone()
        return updated_item._mapping

# Eliminar un elemento de la tabla
@app.delete("/items/{item_id}", response_model=Item)
def delete_item(item_id: int):
    with SessionLocal() as session:
        query = select(items).where(items.c.id == item_id)
        deleted_item = session.execute(query).fetchone()
        if deleted_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        session.execute(items.delete().where(items.c.id == item_id))
        session.commit()
        return deleted_item._mapping

# Buscar elementos por nombre parcial
@app.get("/items/search/{query}", response_model=list[Item])
def search_items(query: str):
    with SessionLocal() as session:
        query = select(items).where(items.c.name.ilike(f"%{query}%"))
        results = session.execute(query).fetchall()
        return [result._mapping for result in results]

# Obtener elementos con paginación
@app.get("/items/", response_model=list[Item])
def get_items(skip: int = 0, limit: int = 10):
    with SessionLocal() as session:
        query = select(items).offset(skip).limit(limit)
        results = session.execute(query).fetchall()
        return [result._mapping for result in results]


# ngrok_tunnel = ngrok.connect(8000)
# print('Public URL:', ngrok_tunnel.public_url)