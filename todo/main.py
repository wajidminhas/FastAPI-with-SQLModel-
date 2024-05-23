

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, Annotated
from todo import settings
from contextlib import asynccontextmanager


class Todo(SQLModel, table=True):
    __tablename__ = "todos"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)

conn_str = str(settings.DATABASE_URL_P).replace(
    "postgresql", "postgresql+psycopg"
)
engine = create_engine(conn_str,  pool_recycle=300)

def create_db_table()->None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Application is starting")
    create_db_table()
    yield
    print("table created") 

        

app:FastAPI = FastAPI(lifespan=lifespan, 
                      title="Todo App",
                        servers=[
                            {
                                "url" : "http://127.0.0.1:8000",
                                "Description" : "development server"
                            }
                        ])

@app.get("/")
async def get_root():
    return {"Message": "Hello developers"}

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