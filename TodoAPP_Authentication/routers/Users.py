from fastapi import APIRouter, status, HTTPException, Path
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import Annotated, Required
from fastapi import Depends
from pydantic import BaseModel, Field
from models import Users
from routers.auth import get_current_user,pwd_context

router = APIRouter(
    prefix="/User",
    tags=["User"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UpdatePasswordRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todos = db.query(Users).filter(Users.id == user.get("id")).first()
    return todos

@router.put("/password", status_code=status.HTTP_200_OK)
async def update_password(user: user_dependency, db: db_dependency,  password_request: UpdatePasswordRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(password_request.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    user_model.hashed_password = pwd_context.hash(password_request.new_password)
    db.add(user_model)
    db.commit()
    return user_model