from sqlalchemy import Column, DateTime, Integer, String, LargeBinary
from app.configs.database import Base

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(50))
    cpf = Column(String(20))
    email = Column(String)
    password = Column(String(60))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_active = Column(Integer)
    role = Column(String)
