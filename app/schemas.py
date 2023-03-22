from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, StrictInt, ValidationError, validator
from datetime import timedelta, datetime


class Course(BaseModel):
    course_code: str
    title: str
    description: str
    units: int

    class Config:
        orm_mode = True

class User(BaseModel):
    name: str
    email : EmailStr

class UserCreate(User):
    password : str
    id : Optional[int] = None

class UserOut(User):
    id : int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
    is_instructor : bool

class TokenUser(BaseModel):
    id: int
    is_instructor : bool

class EnrollInstructor(BaseModel):
    course_code: str
    instructor_id : int
    is_coordinator : bool
    is_accepted: bool

    class Config:
        orm_mode = True

class EnrollStudent(BaseModel):
    course_code: str
    reg_num : Optional[int]
    accepted : Optional[bool] = False

class EnrollStudentOut(EnrollStudent):
    id : int
    class Config:
        orm_mode = True

class Assessment(BaseModel):

    title:str
    start_date:datetime
    duration:int
    total_mark:int
    course_id:str
    end_date: Optional[datetime] = None

    @validator('start_date')
    def check_start(cls, v):
        current_time = datetime.now()
        if v < (current_time + timedelta(minutes=20)):
                raise ValueError('assessment should be created or updated atleast an hour before the test')
        return v
    
    @validator('end_date')
    def dates_check(cls, v, values, **kwargs):
        if v != None:
            if 'start_date' in values and v <= values['start_date']:
                raise ValueError('end_date should be greater than start_date')
        return v

class AssessmentOut(Assessment):
    id:int

    class Config:
        orm_mode = True

class Instruction(BaseModel):
    instruction : str

class Instructions(BaseModel):
    assessment_id:int
    instructions: List[str] 

class InstructionOut(Instruction):
    id: int
    assessment_id: int

    class Config:
        orm_mode = True

class Question(BaseModel):
    question:str
    mark:int
    question_type:Literal['multi_choice', 'list_type', 'others']
    assessment_id:int

class QuestionUpdate(BaseModel):
    question:str
    mark:int
    question_type:Literal['multi_choice', 'list_type', 'others']

class QuestionOut(Question):
    id:int

    class Config:
        orm_mode = True

class Option(BaseModel):
    option:str
    is_correct:bool

class OptionOut(Option):
    id:int

    class Config:
        orm_mode = True

class Options(BaseModel):
    question_id:int
    options : List[Option]

class Submission(BaseModel):
    question_id:int
    stu_answer:Optional[str] = None
    stu_answer_id: Optional[int]

class SubmissionUpdate(BaseModel):
    stu_answer:Optional[str] = None
    stu_answer_id: Optional[int]

class Submissions(BaseModel):
    assessment_id:int
    submissions: List[Submission] 

class QuestionAnswer(QuestionOut):
    answers : Optional[List[OptionOut]] = None

class AssessmentReview(Assessment):
    id:int
    questions: Optional[List[QuestionAnswer]] = None
    instructions : Optional[List[InstructionOut]] = None

    class Config:
        orm_mode = True

class AssessmentQuestion(Assessment):
    id:int
    questions: Optional[List[QuestionOut]] = None
    instructions : Optional[List[InstructionOut]] = None

    class Config:
        orm_mode = True



