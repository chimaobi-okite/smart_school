from typing import List
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, BigInteger, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped

from .database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Instructor(Base):
    __tablename__ = "instructors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Course(Base):
    __tablename__ = "courses"

    course_code = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    units = Column(Integer, nullable=False)

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, ForeignKey("courses.course_code", ondelete="CASCADE"), nullable=False)
    reg_num = Column(BigInteger, nullable=False)
    accepted = Column(Boolean, server_default="FALSE", nullable=False)

class CourseInstructor(Base):
    __tablename__ = "course instructors"

    instructor_id = Column(Integer, ForeignKey("instructors.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    course_code = Column(String, ForeignKey("courses.course_code", ondelete="CASCADE"),primary_key=True, nullable=False)
    is_coordinator = Column(Boolean, server_default="FALSE", nullable=False)
    is_accepted = Column(Boolean, server_default="FALSE", nullable=False)

class Assessment(Base):

    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=False)
    total_mark = Column(Integer, nullable=False)
    course_id = Column(String, ForeignKey("courses.course_code", ondelete="CASCADE"), nullable=False)

    questions = relationship("Question", backref="assessment")
    instructions = relationship("Instruction", backref="assessment")

class Instruction(Base):
    __tablename__ = "instructions"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    instruction = Column(String, nullable=False)

class Question(Base):

    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    question = Column(String, nullable=False)
    mark = Column(Integer, nullable=False)
    # is_multi_choice = Column(Boolean, server_default="FALSE", nullable=False)
    question_type = Column(String, nullable=False)
    
    __table_args__ = (CheckConstraint(question_type.in_(['multi_choice', 'list_type', 'others'])), )
    answers = relationship("Option", backref="question")


class Option(Base):

    __tablename__ = "options"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    option = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)

class Submission(Base):

    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    stu_answer = Column(String, nullable=True)
    ref_answer_id = Column(Integer, nullable=False)
    stu_answer_id = Column(Integer, nullable=True)

class Score(Base):

    __tablename__ = "scores"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(BigInteger, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint('assessment_id','student_id', 'question_id', name='_assessment_student_question_uc'),
                     )


    