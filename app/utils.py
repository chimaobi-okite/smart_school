from app import config
import json
import requests
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def query(payload):
    response = requests.post(
        config.API_URL, headers=config.headers, json=payload)
    return response.json()


def score_mapping(score: float):
    if score >= 0.7:
        return 1
    if score >= 0.4 and score < 0.7:
        return 0.5
    return 0
