from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.orm import joinedload, subqueryload, contains_eager

from sqlalchemy import func
# from sqlalchemy.sql.functions import func
from .. import models, schemas, oauth2
from datetime import timedelta, datetime
from ..database import get_db
from ..config import settings


router = APIRouter(
    prefix="/assessments",
    tags=['Assessments']
)

@router.post("/", response_model=schemas.AssessmentReview)
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

@router.put("/{id}", response_model=schemas.AssessmentReview)
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

@router.get("/{id}/review",response_model=schemas.AssessmentReview)
def review_assessment(id:int, db:Session=Depends(get_db),
                    user:schemas.TokenUser = Depends(oauth2.get_current_user)):
    assessment_query = db.query(models.Assessment).filter(models.Assessment.id == id)
    assessment_detail = assessment_query.first()
    if not assessment_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"assessment with id -> {id} not found")
    if user.is_instructor:
        instructor = db.query(models.Assessment).join(
            models.CourseInstructor, models.Assessment.course_id == models.CourseInstructor.course_code
        ).filter(models.CourseInstructor.instructor_id == user.id, models.Assessment.id == id,
                    models.CourseInstructor.is_accepted == True).first()
        if not instructor:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not user.is_instructor:
        student = db.query(models.Assessment).join(
            models.Enrollment, models.Assessment.course_id == models.Enrollment.course_code
        ).filter(models.Enrollment.reg_num == user.id, models.Assessment.id == id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        # only review after some hours
        current_time = datetime.now()
        review_after = assessment_detail.start_date + assessment_detail.duration + timedelta(hours=settings.review_after)
        if review_after < current_time:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                detail="can only create an assignment to start at a time 1 hour ahead of {current_time}")
        
    assessment = db.query(models.Assessment).options(
        joinedload(models.Assessment.instructions)).options(
        joinedload(models.Assessment.questions)).options(
        joinedload(models.Assessment.questions, models.Question.answers)).filter(
        models.Assessment.id == id).first()
    print(assessment)

    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"assessment with id -> {id} not found")
    return assessment

@router.get("/{id}/questions",response_model=schemas.AssessmentQuestion)
def get_assessment_questions(id:int, db:Session=Depends(get_db),
                    user:schemas.TokenUser = Depends(oauth2.get_current_user)):
    assessment_query = db.query(models.Assessment).filter(models.Assessment.id == id)
    assessment_detail = assessment_query.first()
    if not assessment_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"assessment with id -> {id} not found")
    if user.is_instructor:
        instructor = db.query(models.Assessment).join(
            models.CourseInstructor, models.Assessment.course_id == models.CourseInstructor.course_code
        ).filter(models.CourseInstructor.instructor_id == user.id, models.Assessment.id == id,
                    models.CourseInstructor.is_accepted == True).first()
        if not instructor:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not user.is_instructor:
        student = db.query(models.Assessment).join(
            models.Enrollment, models.Assessment.course_id == models.Enrollment.course_code
        ).filter(models.Enrollment.reg_num == user.id, models.Assessment.id == id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        # access questions only within assessment time frame
        current_time = datetime.now()
        end_time = assessment_detail.start_date + assessment_detail.duration
        if (assessment_detail.start_date < current_time) or (current_time > end_time):
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                                detail="can only create an assignment to start at a time 1 hour ahead of {current_time}")
        
    assessment = db.query(models.Assessment).options(
        joinedload(models.Assessment.instructions)).options(
        joinedload(models.Assessment.questions)).filter(
        models.Assessment.id == id).first()
    print(assessment)

    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"assessment with id -> {id} not found")
    return assessment

@router.get("/{id}", response_model=schemas.AssessmentOut)
def get_assessment(id:int, db:Session=Depends(get_db),
                    user:schemas.TokenUser = Depends(oauth2.get_current_user)):
    if user.is_instructor:
        instructor = db.query(models.Assessment).join(
            models.CourseInstructor, models.Assessment.course_id == models.CourseInstructor.course_code
        ).filter(models.CourseInstructor.instructor_id == user.id, models.Assessment.id == id,
                    models.CourseInstructor.is_accepted == True).first()
        if not instructor:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not user.is_instructor:
        student = db.query(models.Assessment).join(
            models.Enrollment, models.Assessment.course_id == models.Enrollment.course_code
        ).filter(models.Enrollment.reg_num == user.id, models.Assessment.id == id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    assessment = db.query(models.Assessment).filter(models.Assessment.id == id).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"assessment with id -> {id} not found")
    return assessment