import pytest
from .. import schemas
from jose import JWTError, jwt
from ..config import settings

def test_root(client):
    res = client.get("/")
    print(res.json())
    assert res.status_code == 200

def test_create_user(client):
    data = {"email":"okite@gmail.com", "password":"1234", 
            "department":"EEE", "faculty":"SEET", "id": 20171035443,"name":"okite"}
    res = client.post("/users/", json=data)
    new_user = schemas.UserOut(**res.json())
    assert res.status_code == 201
    assert new_user.email == "okite@gmail.com"

def test_login_user(client, test_user):
    data = {"username":test_user['email'], "password":test_user['password']}
    res = client.post("/login", data=data)
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=settings.algorithm)
    id: str = payload.get("user_id")
    assert res.status_code == 200
    assert id == test_user['id']