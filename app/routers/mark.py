from fastapi import FastAPI, Form, Response, status, HTTPException, Depends, APIRouter,  File, UploadFile
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from fastapi.encoders import jsonable_encoder

from sqlalchemy import func

from app.ml import predict
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

def mark_obj(df):
    df['score'] = df.apply(lambda x : x['mark'] if (x['ref_answer_id'] == (x['stu_answer_id'])) else 0, axis=1)
    columns = ['assessment_id', 'question_id', 'student_id', 'score']
    return df[columns]

def check_multi_choice_answers(user_answers: Dict[int, List[int]], correct_answers: Dict[int, List[int]]) -> int:
    is_correct = 0

    for question_id, correct_answer in correct_answers.items():
        user_answer = user_answers.get(question_id, [])
        
        if set(user_answer) == set(correct_answer):
            is_correct = 1
            

    return is_correct

def mark_multi_obj(df, assessment_id):
    result_df = pd.DataFrame(columns = ['assessment_id','question_id', 'student_id', 'score'])
    questions = df["question_id"].unique().tolist()
    users = df["student_id"].unique().tolist()
    for question in questions:
        correct_answers = df[df['question_id'] == question]['ref_answer_id'].unique().tolist()
        score = df[df['question_id'] == question]['mark'].iloc[0]
        correct_answers_dict = {question:correct_answers}
        for user in users:
            user_answers = df[(df['question_id'] == question)& (df["student_id"] == user)]['stu_answer_id'].unique().tolist()
            user_answers_dict = {question:user_answers}
            is_correct = check_multi_choice_answers(user_answers_dict, correct_answers_dict)
            result_df = result_df.append({'assessment_id':assessment_id,'question_id':question, 'student_id':user, 'score':is_correct*score},ignore_index = True)
    return result_df

def text_comparison(ref:str, student_ans:str):
    ref = ref.lower()
    student_ans = student_ans.lower()
    if student_ans in ref:
        return 1
    return 0

def mark_sub_obj(df):
    df['score'] = df.apply(lambda x : text_comparison(x['ref_answer'], x['stu_answer']) * x['mark'], axis=1)
    columns = ['assessment_id', 'question_id', 'student_id', 'score']
    return df[columns]

def mark_multiple_sub(df, assessment_id):
    result_df:pd.DataFrame = pd.DataFrame({'assessment_id':pd.Series(dtype='int'),
                                          'question_id':pd.Series(dtype='int'),
                                            'student_id':pd.Series(dtype='int'), 'score':pd.Series(dtype='float')})
    questions = df["question_id"].unique().tolist()
    users = df["student_id"].unique().tolist()
    for question in questions:
        correct_answers = df[df['question_id'] == question]["ref_answer"].unique().tolist()
        mark = df[df['question_id'] == question]['mark'].iloc[0]
        num_answer = int(df[df['question_id'] == question]['num_answer'].iloc[0])
        correct_answers_dict = {question:correct_answers}
        for user in users:
            user_answers = df[(df['question_id'] == question)& (df["student_id"] == user)]['stu_answer'].unique().tolist()
            user_answers_dict = {question:user_answers}
            sum_score = check_sub_answers(user_answers_dict, correct_answers_dict)
            result_df = result_df.append({'assessment_id':assessment_id,'question_id':question, 'student_id':user, 'score':sum_score*mark/num_answer},ignore_index = True)
    return result_df

def check_sub_answers(user_answers: Dict[int, List[str]], correct_answers: Dict[int, List[str]]) -> int:
    sum_score = 0

    for question_id, correct_answer in correct_answers.items():
        user_answer = user_answers.get(question_id, [])
        for answer in correct_answer:
            for stu_answer in user_answer:
                score = text_comparison(answer, stu_answer)
                sum_score += score
        
    return sum_score

def create_nlp_row_dict(user_answers: Dict[int, List[str]], correct_answers: Dict[int, List[str]],assessment_id:int,student_id:int) -> Dict:

    for question_id, correct_answer in correct_answers.items():
        user_answer = user_answers.get(question_id, [])
        for answer in correct_answer:
            for stu_answer in user_answer:
                row = {"assessment_id":assessment_id,"question_id":question_id,
                       "student_id":student_id, "ref_answer":answer, "stu_answer":stu_answer}
        
    return row

def mark_multiple_nlp(df, assessment_id):
    nlp_df:pd.DataFrame = pd.DataFrame(columns = ['assessment_id','question_id', 'student_id', 'ref_answer', 'stu_answer', 'num_answer', 'mark'])
    questions = df["question_id"].unique().tolist()
    users = df["student_id"].unique().tolist()
    for question in questions:
        correct_answers = df[df['question_id'] == question]["ref_answer"].unique().tolist()
        num_answer = int(df[df['question_id'] == question]['num_answer'].iloc[0])
        mark = df[df['question_id'] == question]['mark'].iloc[0]
        correct_answers_dict = {question:correct_answers}
        for user in users:
            user_answers = df[(df['question_id'] == question)& (df["student_id"] == user)]['stu_answer'].unique().tolist()
            user_answers_dict = {question:user_answers}
            #row = create_nlp_row_dict(user_answers_dict,correct_answers_dict, assessment_id, user)
            for question_id, correct_answer in correct_answers_dict.items():
                user_answer = user_answers_dict.get(question_id, [])
                for answer in correct_answer:
                    for stu_answer in user_answer:
                        row = {"assessment_id":assessment_id,"question_id":question_id,
                            "student_id":user,"num_answer":num_answer, "ref_answer":answer,
                              "stu_answer":stu_answer, "num_answer":num_answer, "mark":mark}
                        nlp_df = nlp_df.append(row, ignore_index = True)
    # nlp_df["assessment_id"].fillna(assessment_id, inplace=True)
    nlp_df['preds'] = predict.predict(nlp_df,  'ref_answer', 'stu_answer')/2
    print(predict.predict(nlp_df,  'ref_answer', 'stu_answer')/2)
    score_df = process_multi_nlp(nlp_df, assessment_id=assessment_id)
    return score_df

def process_multi_nlp(df:pd.DataFrame, assessment_id):
    score_df:pd.DataFrame = pd.DataFrame({'assessment_id':pd.Series(dtype='int'),
                                          'question_id':pd.Series(dtype='int'),
                                            'student_id':pd.Series(dtype='int'), 'score':pd.Series(dtype='float')})
    
    questions = df["question_id"].unique().tolist()
    users = df["student_id"].unique().tolist()
    for question_id in questions:
        num_answer = df[df['question_id'] == question_id]['num_answer'].iloc[0]
        print(num_answer)
        mark = df[df['question_id'] == question_id]['mark'].iloc[0]
        print(mark)
        for user in users:
            score = df[(df['question_id']== question_id) & (df['student_id'] == user)].sort_values(by="preds", ascending=False)['preds'][:num_answer].sum()
            score = score/num_answer * mark
            row = {"assessment_id":assessment_id,"question_id":question_id,
                            "student_id":user,"score":score}
            score_df = score_df.append(row, ignore_index = True)

    return score_df

def mark_single_nlp(df, ref_answer_key, stu_answer_key):
    y_preds = predict.predict(df, ref_answer_key, stu_answer_key)
    df['score'] = df['mark'] * (y_preds/2)
    columns = ['assessment_id', 'question_id', 'student_id', 'score']
    return df[columns]

def mark_maths(df:pd.DataFrame, assessment_id:str):
    df['tolerance'] = df['tolerance'].fillna(0)
    columns = ['assessment_id', 'question_id', 'student_id', 'score']
    df['score'] = df.apply(lambda x : x['mark'] if ((float(x['stu_answer']) >= (float(x['ref_answer']) - x['tolerance'])) and 
                           (float(x['stu_answer']) <= (float(x['ref_answer']) + x['tolerance']))) else 0, axis=1)
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
    # print(db.query(models.Submission.ref_answer_id).filter(
    #     models.Submission.assessment_id == id).all())
    submissions = db.query(models.Assessment.id, models.Question.id, 
             models.Question.mark, models.Question.question_type, models.Question.is_multi_choice, 
             models.Question.tolerance,models.Question.num_answer, models.Option.id, models.Option.option, models.Submission.student_id,
             models.Submission.stu_answer, models.Submission.stu_answer_id).join(
        models.Question, models.Assessment.id == models.Question.assessment_id).join(
        models.Option, models.Question.id == models.Option.question_id).join(
        models.Submission, models.Submission.question_id == models.Question.id
    ).filter(models.Option.is_correct == True, models.Submission.assessment_id == id).all()
    # submissions = db.query(models.Submission.assessment_id,models.Submission.question_id,
    #                        models.Submission.student_id,models.Submission.stu_answer,
    #                        models.Submission.stu_answer_id,models.Option.id,
    #                        models.Question.mark, models.Question.question_type, models.Question.answer_type).join(
    #     models.Question, models.Submission.question_id == models.Question.id).join(
    #     models.Option, models.Option.question_id == models.Question.id
    #     ).filter(
    #     models.Submission.assessment_id == id, models.Option.is_correct == True).all()
    columns = ['assessment_id', 'question_id', 'mark','question_type', 'is_multi_choice','tolerance','num_answer','ref_answer_id', 'ref_answer','student_id', 
               'stu_answer', 'stu_answer_id',]
    # columns = ['assessment_id', 'question_id','student_id', 
    #            'stu_answer', 'stu_answer_id', 'ref_answer_id', 'mark','question_type', 'answer_type',]
    sub_df = pd.DataFrame.from_records(submissions,
                                                columns=columns)
    print(sub_df)
    # print(sub_df.stu_answer_id.values)
    obj_df = sub_df[(sub_df.question_type == 'obj') &(sub_df.is_multi_choice == False)]
    multi_obj_df = sub_df[(sub_df.question_type == 'obj')&(sub_df.is_multi_choice == True)]
    sub_obj_df = sub_df[(sub_df.question_type == 'sub_obj')&(sub_df.is_multi_choice == False)]
    sub_obj_multi_df = sub_df[(sub_df.question_type == 'sub_obj')&(sub_df.is_multi_choice ==True )]
    nlp_single_df = sub_df[(sub_df.question_type == 'nlp')&(sub_df.is_multi_choice == False )]
    nlp_multiple_df = sub_df[(sub_df.question_type == 'nlp')&(sub_df.is_multi_choice ==True )]
    maths_df = sub_df[(sub_df.question_type == 'maths')]
    print(nlp_single_df)
    # sub_obj_df = sub_df[sub_df.question_type == 'sub_obj']
    # nlp_df = sub_df[sub_df.question_type == 'nlp']
    obj_score_df = mark_obj(obj_df)
    multi_obj_score_df = mark_multi_obj(multi_obj_df, assessment_id = id)
    sub_obj_score_df = mark_sub_obj(sub_obj_df)
    sub_obj_multiple_df = mark_multiple_sub(sub_obj_multi_df, assessment_id=id)
    # nlp_score_df = mark_nlp(nlp_df, assessment_id=id)
    maths_score_df = mark_maths(maths_df, assessment_id= id)
    print(obj_score_df)
    print(multi_obj_score_df)
    print(sub_obj_score_df)
    print(sub_obj_multiple_df)
    print(maths_score_df)
    single_nlp_scores = mark_single_nlp(nlp_single_df,'ref_answer', 'stu_answer' )
    print(single_nlp_scores)
    multiple_nlp_scores = mark_multiple_nlp(nlp_multiple_df,assessment_id=id)
    print(multiple_nlp_scores)
    df_list = [obj_score_df,multi_obj_score_df,
                sub_obj_score_df, sub_obj_multiple_df, maths_score_df, single_nlp_scores, multiple_nlp_scores]
    score_df = pd.concat(df_list, axis=0)

    #change data-type
    convert_dict = {'assessment_id': int,'question_id': int,'student_id':'int64', 'score':float}
    score_df = score_df.astype(convert_dict)
    scores = score_df.to_dict('records')
    stu_scores = []
    for score in scores:
        score = models.Score(**score)
        stu_scores.append(score)
    db.add_all(stu_scores)
    db.commit()