import os
from pydantic import BaseSettings


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_DIR = os.path.join(ROOT_DIR, "photos")
TRANSFORMER_MODEL_NAME = 'paraphrase-MiniLM-L6-v2'

USER_NAME = 'okitesam'
PROJECT_NAME = 'my-lightgbm-project2'
SWEEP_ID = 'gsrfuosb'
MODEL_NAME = 'LBGMClassifier:v14'
MODEL_PATH_NAME = 'lgbm_class.model.pkl'
ML_DIR_PATH = os.path.join(ROOT_DIR, "ml")
MODEL_DIR_PATH = os.path.join(ML_DIR_PATH, "models")
ML_MODEL_DIR = os.makedirs(MODEL_DIR_PATH, exist_ok=True)
ML_MODEL_PATH = os.path.join(MODEL_DIR_PATH, "lgbm_class.model.pkl")

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    review_after:int
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()