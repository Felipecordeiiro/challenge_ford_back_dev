from typing import Annotated
from fastapi import FastAPI, Depends
from app.configs.config import configurar_banco
from fastapi.middleware.cors import CORSMiddleware
from app.configs.database import get_db
from app.routers import analytical, location, part, purchase, supplier, vehicle, warranty, auth
from app.configs.auth import get_current_active_user
from sqlalchemy.orm import Session
import os

from app.models.model_vehicle import Vehicle
from app.models.model_location import Location
from app.models.model_supplier import Supplier
from app.models.model_purchase import Purchase
from app.models.model_part import Part
from app.models.model_warranty import Warranty
from app.models.model_user import User
from app.models.model_token import Token


app = FastAPI()

# USER DEPENDENCIES
user_dependency = Annotated[dict, Depends(get_current_active_user)]

# DATABASE SETUP
DATABASE_URL = os.getenv("DATABASE_URL")
configurar_banco(DATABASE_URL)

# CORS
origins = [
    "http://localhost:3000",  # Front-end local
    "http://localhost:8000",  # Swagger
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/", status_code=200)
async def main(user: user_dependency, db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=401, detail="Autenticação falhou")
    return {"message": f"{user}\nFastAPI + PostgreSQL rodando no Docker!"}

app.include_router(auth.router)
app.include_router(supplier.router)
app.include_router(purchase.router)
app.include_router(analytical.router)
app.include_router(part.router)
app.include_router(location.router)
app.include_router(warranty.router)
app.include_router(vehicle.router)

if "__name__" == "__main__":
    main()
