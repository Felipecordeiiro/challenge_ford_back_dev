from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import os

from app.configs.database import get_db
from app.schemas.auth import TokenDataModel
from app.schemas.user import IsActiveEnum, UserInDBModel, UserModel
from app.utils.auth import get_user_by_user_name, verify_password
from app.errors import DecodeTokenException, EncodingTokenException, InvalidCredentials, InvalidTokenException, TokenExpiredException
from app.models.model_user import User

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

def decode_token(token: str) -> dict:
    try:  
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        # Verificar se o token contém os dados necessários
        if "user_id" not in payload:
            raise InvalidTokenException
        
        # Se o token tiver um campo exp (expiration), verificar se já expirou
        if "exp" in payload:
            exp_timestamp = payload["exp"]
            current_timestamp = datetime.utcnow().timestamp()
            
            if current_timestamp > exp_timestamp:
                raise TokenExpiredException
        
        return payload
    
    except JWTError:
        raise InvalidCredentials
        
    except Exception as e:
        raise DecodeTokenException(e)
    
def create_token(user_data: dict, refresh: bool = False) -> str:
    try:
        
        to_encode = {}
        to_encode["user"] = user_data
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire_at = datetime.utcnow() + expires_delta
        to_encode["exp"] = expire_at

        to_encode["refresh"] = refresh

        return jwt.encode(
            to_encode, 
            SECRET_KEY, 
            algorithm=ALGORITHM
        )
    except Exception as e:
        raise EncodingTokenException(e)
    
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        if 'user_name' not in payload and 'mode' not in payload:
            raise InvalidCredentials
        if payload['mode'] != 'refresh_token':
            raise InvalidCredentials
        user = get_user_by_user_name(username, db)
        if username is None:
            raise HTTPException(status_code=401, detail="Usuário inválido.")
        
        token_data = TokenDataModel(username=username)
    except JWTError:
        raise InvalidCredentials

    user = get_user_by_user_name(token_data.username, db)

    if user is None:
        raise InvalidCredentials
    
    return user

async def get_current_active_user(current_user: UserInDBModel = Depends(get_current_user)) -> UserModel:
    if current_user.is_active == IsActiveEnum.deactivated:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user

def authenticate_user(db, username: str, password: str):
    user = get_user_by_user_name(username, db)
    if not user:
        raise HTTPException(status_code=401, detail=f"Usuário ou senha inválido.")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail=f"Senha inválida. \nuser.password: {user.password}\npassword: {password}")
    return user