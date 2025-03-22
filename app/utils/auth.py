from fastapi import Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.configs.database import get_db
from app.models.model_user import User
from app.models.model_token import Token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_cpf(cpf:str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.cpf == cpf).first()

def get_user_by_user_name(user_name:str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.user_name == user_name).first()

def get_user_by_email(email:str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(user_id:str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.user_id == user_id).first()

def get_token_by_user_id(user_id: int, refresh_token: str, db: Session = Depends(get_db)):
    return db.query(Token).filter(Token.user_id == user_id, Token.refresh_token == refresh_token)

def hashed_password(password:str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)