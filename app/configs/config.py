from sqlalchemy import create_engine
from app.configs.database import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL")
TEST_DATABASE = os.getenv('TEST_DATABASE', 'false') in ('true', 'yes')
os.environ['TEST_DATABASE'] = 'false'

def configurar_banco(database_url = DATABASE_URL, force_drop=False):
    engine = create_engine(database_url)

    # Apenas dropa todas as tabelas se estiver em ambiente de teste ou se forçado
    is_test = os.getenv('TEST_DATABASE', 'false') in ('true', 'yes')
    if is_test or force_drop:
        Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine) 
    print("Banco de dados configurado!")