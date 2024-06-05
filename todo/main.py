

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Annotated
from contextlib import asynccontextmanager
from todo.auth import authenticate_user, get_user_from_db
from todo.model import Todo
from todo.db import create_db_table, get_session
from todo.router import user



@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Application is starting")
    create_db_table()
    yield
    print("table created") 

        

app:FastAPI = FastAPI(
                    lifespan=lifespan, 
                      title="Todo App",
                        )
app.include_router(router= user.user_router)

@app.get("/")
async def get_root():
    return {"Message": "Hello developers"}

@app.post("/token")
async def login(form_data:Annotated[OAuth2PasswordRequestForm, Depends()],
                    session:Annotated[Session, Depends(get_session)]):
    user = authenticate_user(name=form_data.username, password=form_data.password, email=None, session=session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user

    

    # POST REQUEST CREATED 
@app.post("/todos",response_model=Todo) 
async def create_todo(todo: Todo, session : Annotated[Session, Depends( get_session)]):
    session.add(todo)
    session.commit()
    session.refresh(todo)

    return todo

@app.get("/todos/{id}", response_model=Todo)
async def get_single_task(id: int, session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo).where(Todo.id == id)).first()
    return todos

@app.get("/todos", response_model=list[Todo])
async def get_all_tasks(session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo)).all()
    return todos