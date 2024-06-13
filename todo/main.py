

from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, logger
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Annotated
from contextlib import asynccontextmanager
from todo.auth import authenticate_user
from todo.model import Todo, Token, User
from todo.db import create_db_table, get_session
from todo.router import user
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from todo import settings
import asyncio
from todo import todo_pb2
import logging


class Todo(SQLModel):
    id: int = Field(default=None)
    content:str
    


async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()


async def consume_message(topic, bootstrap_servers):
    consume = AIOKafkaConsumer(topic,
                              bootstrap_servers=bootstrap_servers,
                              group_id="my_group",
                              auto_offset_reset="earliest")
    await consume.start()
    try:
        async for message in consume:
            print(f"Consumed message Before Deserialized: {message.value}")
            try:
                new_todo = todo_pb2.Todo()
                new_todo.ParseFromString(message.value)
                print(f"Deserialized Todo: {new_todo}")
                print(f"Deserialized Todo: {new_todo}")
            except Exception as e:
                print(f"Failed to deserialize message: {e}")
    finally:
        await consume.stop()

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Application is starting")
    task = asyncio.create_task(consume_message(settings.KAFKA_ORDER_TOPIC, settings.KAFKA_BOOTSTRAP_SERVER))
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


# ********************   # USER AUTHENTICATION    **************************** 
@app.post("/token")
async def user_profile_authenticate(form_data:Annotated[OAuth2PasswordRequestForm, Depends()],
                                    session:Annotated[Session, Depends(get_session)], ):
    user = authenticate_user(username=form_data.username, password=form_data.password,
                             email=None, session=session )
    if not user:
        raise HTTPException(status_code=401, detail="incorrect username or email")
    return user
    

    # POST REQUEST CREATED 
# @app.post("/todos",response_model=Todo) 
# async def create_todo(current_user:Annotated[User, Depends(current_user)],
#                       todo: Todo, session : Annotated[Session, Depends( get_session)]):
#     session.add(todo)
#     session.commit()
#     session.refresh(todo)

#     return todo

@app.get("/todos/{id}", response_model=Todo)
async def get_single_task(id: int, session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo).where(Todo.id == id)).first()
    return todos

@app.get("/todos", response_model=list[Todo])
async def get_all_tasks(session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo)).all()
    return todos


@app.post("/create_todo")
async def create_order(todo: Todo, session : Annotated[Session, Depends(get_session)],
                       producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    # producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVER)
    # await producer.start()
    # orderJSON = json.dumps(todo.__dict__).encode("utf-8")
    # print("Todo Json")
    # print(orderJSON)  

    todos_protobuf = todo_pb2.Todo(id=todo.id, content=todo.content)
    print(f"Proto Buffer : {todos_protobuf}")
    # serliazed message into a byte string
    serlized_todo = todos_protobuf.SerializeToString()
    print(f"Serialized Todo : {serlized_todo}")
    try:
        await producer.send_and_wait(settings.KAFKA_ORDER_TOPIC, serlized_todo)
    finally:
        await producer.stop()

    return todo
    
