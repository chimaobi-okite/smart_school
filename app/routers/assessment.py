from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
# from sqlalchemy.sql.functions import func
from .. import models, schemas, oauth2
from datetime import timedelta, datetime
from ..database import get_db


router = APIRouter(
    prefix="/assessments",
    tags=['Assessments']
)

@router.post("/", response_model=schemas.AssessmentOut)
def create_assessment(assessment:schemas.Assessment, db:Session=Depends(get_db),
                        user:schemas.TokenUser = Depends(oauth2.get_current_user)):
    instructor = db.query(models.CourseInstructor).filter(
        models.CourseInstructor.course_code == assessment.course_id,
        models.CourseInstructor.is_accepted == True,
        models.CourseInstructor.instructor_id == user.id).first()
    if not instructor:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied")
    
    # only create assessment two hours into the future
    current_time = datetime.now()
    if assessment.start_date < (current_time + timedelta(minutes=20)):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail="can only create an assignment to start at a time 1 hour ahead of {current_time}")
    new_assessment = models.Assessment(**assessment.dict())
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)
    return new_assessment

@router.put("/{id}", response_model=schemas.AssessmentOut)
def update_assessment(updated_assessment:schemas.Assessment,id:int, db:Session=Depends(get_db),
                        user:schemas.TokenUser = Depends(oauth2.get_current_user)):
    instructor = db.query(models.CourseInstructor).filter(
        models.CourseInstructor.course_code == updated_assessment.course_id,
        models.CourseInstructor.is_accepted == True,
        models.CourseInstructor.instructor_id == user.id).first()
    
    if not instructor:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied")
    assessment_query = db.query(models.Assessment).filter(models.Assessment.id == id)
    assessment_detail = assessment_query.first()
    if not assessment_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"assessment with id -> {id} not found")
    
    current_time = datetime.now()
    if assessment_detail.start_date < (current_time + timedelta(minutes=20)):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail="cannot update already started, ended assessments or update 15 minutes before start time")
    if updated_assessment.start_date < (current_time + timedelta(minutes=20)):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                            detail=f"can only update an assignment to start at a time 1 hour ahead of {current_time}")
    assessment_query.update(updated_assessment.dict(), synchronize_session=False)
    db.commit()
    db.refresh(assessment_query.first())
    return assessment_query.first()

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assessment(id:int, db:Session=Depends(get_db), 
                      user:schemas.TokenUser=Depends(oauth2.get_current_user)):
    assessment_query = db.query(models.Assessment).filter(models.Assessment.id == id)
    assessment_detail = assessment_query.first()
    if not assessment_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"assessment with id -> {id} not found")
    instructor = db.query(models.Assessment).join(
        models.CourseInstructor, models.Assessment.course_id == models.CourseInstructor.course_code).filter(
        models.Assessment.id == id,
        models.CourseInstructor.instructor_id == user.id,
        models.CourseInstructor.is_accepted == True).first()
    if not instructor:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied")
    assessment_query.delete(synchronize_session=False)
    db.commit()