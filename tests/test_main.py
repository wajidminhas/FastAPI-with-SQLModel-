import pytest
from fastapi.testclient import TestClient
from fastapi import status
from todo.main import app
from todo import settings
from sqlmodel import SQLModel, create_engine

conn_str = str(settings.TODO_DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)
engine = create_engine(conn_str,  pool_recycle=300)

def get_root():
    client = TestClient(app=app)
    response = client.get("/")
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data == {"Message": "Hello developers"}
