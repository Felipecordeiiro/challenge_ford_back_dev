from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Header, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os

from app.errors import InvalidTokenException, RefreshTokenException, TokenNotFoundException, UserNotFound
from app.models.model_user import User
from app.schemas.auth import TokenTypeEnum
from app.schemas.user import UserInDBModel, UserModel
from app.configs.auth import authenticate_user, create_token, decode_token
from app.utils.auth import get_token_by_user_id, get_user_by_id, hashed_password
from app.configs.database import get_db
from app.models.model_token import Token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserInDBModel, db: Session = Depends(get_db)) -> UserModel:
    hash_password = hashed_password(user.password)
    new_user = User(
        user_name = user.user_name,
        cpf = user.cpf,
        email = user.email,
        password = hash_password,
        created_at = user.created_at,
        updated_at = user.updated_at,
        is_active = user.is_active,
        role = user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserModel(**new_user.__dict__)

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    username = form_data.username
    password = form_data.password
    
    user = authenticate_user(db, username, password)
    
    access_token = create_token(user_data={
        "email": user.email, "user_id": user.user_id, "role": user.role
        }
    )

    refresh_token = create_token(user_data={
        "email": user.email, "user_id": user.user_id, "role": user.role},
        refresh=True
    )
    current_data = datetime.utcnow()
    expires_at = current_data + timedelta(minutes=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")))

    db_token = Token(
        user_id = user.user_id,
        token_type = TokenTypeEnum.bearer,
        access_token = access_token,
        refresh_token = refresh_token,
        expires_at = expires_at,
        created_at = current_data
    )

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return JSONResponse(
            content={
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "username": user.user_name,
                    "email": user.email,
                    "role": user.role,
                    "Expira em": expires_at.isoformat()
                },
            }
        )

@router.get("/refresh_token")
async def get_new_access_token(refresh_token: str = Header(...), db: Session = Depends(get_db)) -> dict:
    """
    Gera novos tokens a partir de um refresh token válido.
    O cliente precisa apenas enviar o refresh_token no header.
    """
    try:
        token_data = decode_token(refresh_token)
        user_id = token_data.get("user_id")
        if not user_id:
            raise InvalidTokenException
        
        db_token = get_token_by_user_id(user_id, refresh_token, db)
        
        if not db_token:
            raise TokenNotFoundException
        
        user = get_user_by_id(user_id, db)

        if not user:
            raise UserNotFound(user)

        token_expiry = db_token.expires_at
        current_time = datetime.utcnow()

        if datetime.fromtimestamp(token_expiry) > current_time:
            new_access_token = create_token(user_data={"email": user.email, "user_id": user.user_id, "role": user.role})
            new_refresh_token = create_token(user_data={"email": user.email, "user_id": user.user_id, "role": user.role}, refresh=True)

            new_token_record = Token(
                user_id = user.user_id,
                token_type = TokenTypeEnum.bearer,
                access_token = new_access_token,
                refresh_token = new_refresh_token,
                expires_at= current_time + timedelta(minutes=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))),
                created_at= current_time
            )
            db.add(new_token_record)
            db.commit()
            
            if token_expiry <= current_time:
                message = "Previous token was expired. New tokens generated."
            else:
                message = "New tokens generated successfully."

            return JSONResponse(content={
                "message": message,
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "expires_at": new_token_record.expires_at.isoformat()
            })
    except Exception as e:
        raise RefreshTokenException(e)
