from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from app.configs.database import Base

class Token(Base):
    __tablename__ = 'tokens'

    token_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    token_type = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    expires_at = Column(DateTime)
    created_at = Column(DateTime)