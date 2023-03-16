from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
# from sqlalchemy.sql.functions import func
from .. import models, schemas, oauth2
from ..database import get_db


router = APIRouter(
    prefix="/courses",
    tags=['Courses']
)

@router.post("/", response_model=schemas.Course)
def create_course(course:schemas.Course, db:Session=Depends(get_db), user: schemas.TokenUser = Depends(oauth2.get_current_user)):
    if not user.is_instructor:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not unauthorized to perform request")
    exists = db.query(models.Course).filter(models.Course.course_code == course.course_code).count() > 0
    if exists:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail=f"course with code {course.course_code} already exists")
    new_course = models.Course(**course.dict())

    instructor = schemas.EnrollInstructor(course_code=course.course_code,
                                              instructor_id=user.id, is_coordinator=True, is_accepted=True)
    instructor = models.CourseInstructor(**instructor.dict())
    db.add(instructor)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("/", response_model=List[schemas.Course])
def get_courses(db:Session=Depends(get_db),user: schemas.TokenUser = Depends(oauth2.get_current_user)):
    courses = db.query(models.Course).all()
    return courses

@router.get("/{code}", response_model=schemas.Course)
def get_courses(code: str, db:Session=Depends(get_db),user: schemas.TokenUser = Depends(oauth2.get_current_user)):
    course = db.query(models.Course).filter(models.Course.course_code == code).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail=f"course with code {code} already exists")
    return course