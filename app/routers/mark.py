from fastapi import FastAPI, Form, Response, status, HTTPException, Depends, APIRouter,  File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from sqlalchemy import func
# from sqlalchemy.sql.functions import func
from .. import models, schemas, oauth2
from ..database import get_db
import pandas as pd
import numpy as np
from datetime import timedelta, datetime

router = APIRouter(
    prefix="/marks",
    tags=['Mark']
)

def mark_multichoice(df):
    print(len(df)) 
    # print(df['ref_answer_id'].equals(df['stu_answer_id']))
    # df['score'] = np.where((df['ref_answer_id'] == df['stu_answer_id']),df['mark'],0)
    df['score'] = df.apply(lambda x : x['mark'] if (df['ref_answer_id'].equals(df['stu_answer_id'])) else 0, axis=1)
    columns = ['assessment_id', 'question_id', 'student_id', 'score']
    return df[columns]

def mark_others(df):
    print(len(df)) 
    df["score"] = 4/5 * df["mark"]
    columns = ['assessment_id', 'question_id', 'student_id', 'score']
    return df[columns]

@router.post("/{id}")
def mark_assessment(id:int, db:Session=Depends(get_db),
                    user:schemas.TokenUser = Depends(oauth2.get_current_user)):
    if not user.is_instructor:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    instructor = db.query(models.Assessment).join(
        models.CourseInstructor, models.Assessment.course_id == models.CourseInstructor.course_code
    ).filter(models.CourseInstructor.instructor_id == user.id, models.Assessment.id == id,
                models.CourseInstructor.is_accepted == True).first()
    if not instructor:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    assessment_query = db.query(models.Assessment).filter(models.Assessment.id == id)
    assessment_detail = assessment_query.first()
    if not assessment_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"assessment with id -> {id} not found")
    current_time = datetime.now()
    end_time = assessment_detail.start_date + timedelta(minutes=(assessment_detail.duration + 60))
    print(end_time)
    # if current_time < end_time:
    #     raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
    print(db.query(models.Submission.ref_answer_id).filter(
        models.Submission.assessment_id == id).all())
    submissions = db.query(models.Submission.assessment_id,models.Submission.question_id,
                           models.Submission.student_id,models.Submission.stu_answer,
                           models.Submission.stu_answer_id,models.Submission.ref_answer_id,
                           models.Question.mark, models.Question.is_multi_choice).join(
        models.Question, models.Submission.question_id == models.Question.id).filter(
        models.Submission.assessment_id == id).all()
    columns = ['assessment_id', 'question_id', 'student_id', 
               'stu_answer', 'stu_answer_id','ref_answer_id','mark','is_multi_choice']
    sub_df = pd.DataFrame.from_records(submissions,
                                                columns=columns)
    print(sub_df.stu_answer_id.values)
    multi_df = sub_df[sub_df.is_multi_choice == True]
    other_df = sub_df[sub_df.is_multi_choice == False]
    multi_score_df = mark_multichoice(multi_df)
    other_score_df = mark_others(other_df)
    print(multi_score_df)
    print(other_score_df)