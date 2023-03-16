from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
# from sqlalchemy.sql.functions import func
from .. import models, schemas, oauth2
from ..database import get_db
from app import utils


router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    if user.id == None:
        new_user = models.Instructor(**user.dict())
    else:
        new_user = models.Student(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db), ):
    user = db.query(models.Instructor).filter(models.Instructor.id == id).first()
    if not user:
        user = db.query(models.Student).filter(models.Student.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")

    return user

@router.get('/')
def get_user(user = Depends(oauth2.get_current_user)):
    return user