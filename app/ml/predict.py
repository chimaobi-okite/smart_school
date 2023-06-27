import os
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import torch.nn as nn
import torch
from sentence_transformers import SentenceTransformer
import wandb
from .. import config

# os.environ['CURL_CA_BUNDLE'] = ''
transformer_model = SentenceTransformer(config.TRANSFORMER_MODEL_NAME)

def download_artifact():
  run = wandb.init(project=config.PROJECT_NAME, settings=wandb.Settings(_service_wait=300))
  artifact = run.use_artifact(f"{config.USER_NAME}/{config.PROJECT_NAME}/{config.MODEL_NAME}", type='model')
  artifact_dir = artifact.download()
  model_path = os.path.join(artifact_dir, config.MODEL_PATH_NAME)
  print(model_path)
  print(artifact_dir)
  model = joblib.load(model_path)
  joblib.dump(model, config.ML_MODEL_PATH)
  return model

def preprocess(df:pd.DataFrame, ref_answer_key:str,stu_answer_key:str):
  sentences1 = list(df[ref_answer_key].values)
  sentences2 = list(df[stu_answer_key].values)
  u = transformer_model.encode(sentences1)
  v = transformer_model.encode(sentences2)

  cos = nn.CosineSimilarity(dim=1, eps=1e-6)
  sim = cos(torch.from_numpy(u), torch.from_numpy(v)).numpy()
  sim = np.expand_dims(sim, axis = 1)
  print(sim.shape)
  embs = np.hstack((u,v,u-v))
  embs = np.concatenate((embs, sim), axis = 1)
  print(embs.shape)
  return embs

def predict(df:pd.DataFrame, ref_answer_key:str,stu_answer_key:str):
  embs = preprocess(df, ref_answer_key, stu_answer_key)
  if not os.path.exists(config.ML_MODEL_PATH):
    download_artifact()
  model = joblib.load(config.ML_MODEL_PATH)
  y_preds = model.predict(embs)
  return y_preds