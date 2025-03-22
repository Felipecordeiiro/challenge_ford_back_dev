from sqlalchemy import create_engine
from app.configs.database import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL")
TEST_DATABASE = os.getenv('TEST_DATABASE', 'false') in ('true', 'yes')

def configurar_banco(database_url = DATABASE_URL):
    engine = create_engine(database_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine) 
    print("Banco de dados configurado!")