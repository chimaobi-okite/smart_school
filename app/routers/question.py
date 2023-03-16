from fastapi import FastAPI, Form, Response, status, HTTPException, Depends, APIRouter,  File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
# from sqlalchemy.sql.functions import func
from .. import models, schemas, oauth2
from ..database import get_db


router = APIRouter(
    prefix="/questions",
    tags=['Questions']
)

@router.post("/", response_model=schemas.QuestionOut)
def create_question(question:schemas.Question, user:schemas.TokenUser=Depends(oauth2.get_current_user),
                    db:Session=Depends(get_db)):
    assessment = db.query(models.Assessment).filter(models.Assessment.id == question.assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="assessment not found")
    instructor = db.query(models.Assessment).join(
        models.CourseInstructor, models.Assessment.course_id == models.CourseInstructor.course_code
    ).filter(models.Assessment.id == question.assessment_id, 
             models.CourseInstructor.instructor_id == user.id,
             models.CourseInstructor.is_accepted == True).first()
    if not instructor:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    new_question = models.Question(**question.dict())
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

@router.put("/{id}", response_model=schemas.QuestionOut)
def update_question(id:int, updated_question:schemas.QuestionUpdate, user:schemas.TokenUser=Depends(oauth2.get_current_user),
                    db:Session=Depends(get_db)):
    question_query = db.query(models.Question).filter(models.Question.id==id)
    if not question_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="question not found")
    instructor = db.query(models.Question).join(
        models.Assessment, models.Question.assessment_id == models.Assessment.id).join(
        models.CourseInstructor, models.Assessment.course_id == models.CourseInstructor.course_code
    ).filter(models.Question.id == id, 
             models.CourseInstructor.instructor_id == user.id,
             models.CourseInstructor.is_accepted == True).first()
    if not instructor:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    question_query.update(updated_question.dict(), synchronize_session=False)
    db.commit()
    db.refresh(question_query.first())
    return question_query.first()

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(id:int,user:schemas.TokenUser=Depends(oauth2.get_current_user),
                    db:Session=Depends(get_db)):
    question_query = db.query(models.Question).filter(models.Question.id==id)
    if not question_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="question not found")
    instructor = db.query(models.Question).join(
        models.Assessment, models.Question.assessment_id == models.Assessment.id).join(
        models.CourseInstructor, models.Assessment.course_id == models.CourseInstructor.course_code
    ).filter(models.Question.id == id, 
             models.CourseInstructor.instructor_id == user.id,
             models.CourseInstructor.is_accepted == True).first()
    if not instructor:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    question_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)