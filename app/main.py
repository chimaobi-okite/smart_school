from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
import cloudinary.uploader
from fastapi.middleware.cors import CORSMiddleware

from app import config

from . import models
from .database import engine
from .routers import course, user, auth, student, instructor, assessment, question, answer, submission, instruction, mark
# from .config import settings


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

cloudinary.config(
    cloud_name=config.settings.cloud_api_name,
    api_key=config.settings.cloud_api_key,
    api_secret=config.settings.cloud_api_secret
)

app.include_router(course.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(instructor.router)
app.include_router(student.router)
app.include_router(assessment.router)
app.include_router(instruction.router)
app.include_router(question.router)
app.include_router(answer.router)
app.include_router(submission.router)
app.include_router(mark.router)


@app.get("/")
def root():
    return {"message": "Hello World pushing out to ubuntu"}
