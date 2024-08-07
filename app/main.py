

from datetime import timedelta, datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, logger
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Annotated
from contextlib import asynccontextmanager
from .auth import EXPIRY_TIME, authenticate_user, create_access_token, current_user
from app.model import  Todo , User, Token
from .model import   TodoUpdate, Token
from .db import create_db_table, get_session
from .router import user
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app import settings
import asyncio
# from app import todo_pb2
import logging


# class Todo(SQLModel):
    # id: int = Field(default=None)
    # content:str
    


# async def get_kafka_producer():
#     producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVER)
#     await producer.start()
#     try:
#         yield producer
#     finally:
#         await producer.stop()


# async def consume_message(topic, bootstrap_servers):
#     consume = AIOKafkaConsumer(topic,
#                               bootstrap_servers=bootstrap_servers,
#                               group_id="my_group",
#                               auto_offset_reset="earliest")
#     await consume.start()
#     try:
#         async for message in consume:
#             print(f"Consumed message Before Deserialized: {message.value}")
#             try:
#                 new_todo = todo_pb2.Todo()
#                 new_todo.ParseFromString(message.value)
#                 print(f"Deserialized Todo: {new_todo}")
#                 print(f"Deserialized Todo: {new_todo}")
#             except Exception as e:
#                 print(f"Failed to deserialize message: {e}")
#     finally:
#         await consume.stop()

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Application is starting")
    # task = asyncio.create_task(consume_message(settings.KAFKA_ORDER_TOPIC, settings.KAFKA_BOOTSTRAP_SERVER))
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
class Token(BaseModel):
    access_token: str
    token_type: str
# ********************   # USER AUTHENTICATION    **************************** 
@app.post("/token", response_model=Token)
async def user_profile_authenticate(form_data:Annotated[OAuth2PasswordRequestForm, Depends()],
                                    session:Annotated[Session, Depends(get_session)], ):
    user = authenticate_user(username=form_data.username, password=form_data.password,
                              session=session )
    if not user:
        raise HTTPException(status_code=401, detail="incorrect username or email")

    access_token_expires = timedelta(minutes=EXPIRY_TIME)
    access_token = create_access_token(
        data={"sub": user.username}, expiry_time=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


    

    # POST REQUEST CREATED 
# @app.post("/todos",response_model=Todo) 
# async def create_todo(current_user:Annotated[User, Depends(current_user)],
#                       todo: Todo, session : Annotated[Session, Depends( get_session)]):
#     session.add(todo)
#     session.commit()
#     session.refresh(todo)

#     return todo



@app.get("/todos", response_model=list[Todo])
async def get_all_tasks(session: Annotated[Session, Depends(get_session)]):
    todos = session.exec(select(Todo)).all()
    return todos


# @app.post("/create_todo")
# async def create_order(todo: Todo, session : Annotated[Session, Depends(get_session)],
#                        producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
#     # producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVER)
#     # await producer.start()
#     # orderJSON = json.dumps(todo.__dict__).encode("utf-8")
#     # print("Todo Json")
#     # print(orderJSON)  

#     todos_protobuf = todo_pb2.Todo(id=todo.id, content=todo.content)
#     print(f"Proto Buffer : {todos_protobuf}")
#     # serliazed message into a byte string
#     serlized_todo = todos_protobuf.SerializeToString()
#     print(f"Serialized Todo : {serlized_todo}")
#     try:
#         await producer.send_and_wait(settings.KAFKA_ORDER_TOPIC, serlized_todo)
#     finally:
#         await producer.stop()
#     session.add(todo)
#     session.commit()

#     session.refresh(todo)
#     print("Todo adding", todo)

#     return todo


# @app.post("/create_todo")
# async def create_order(
#     todo: Todo, 
#     session: Annotated[Session, Depends(get_session)],
#     producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]
# ):
#     todos_protobuf = todo_pb2.Todo(id=todo.id, content=todo.content)
#     print(f"Proto Buffer : {todos_protobuf}")
    
#     serlized_todo = todos_protobuf.SerializeToString()
#     print(f"Serialized Todo : {serlized_todo}")
    
#     try:
#         await producer.send_and_wait(settings.KAFKA_ORDER_TOPIC, serlized_todo)
#     finally:
#         await producer.stop()

#     new_todo = Todo.from_orm(todo)
#     session.add(new_todo)
#     session.commit()
#     session.refresh(new_todo)
#     print("Todo adding", new_todo)

#     return new_todo

    # to create to do



# class TokenData(BaseModel):
#        name : str

# *************   CREATE TODO   *************
class TodoCreate(BaseModel):
    title: str = Field(index=True, min_length=5, max_length=100)

@app.post("/create_todo",  response_model=Todo)
async def create_new_todo(todo: TodoCreate, session: Annotated[Session, Depends(get_session)],
                      current_user: Annotated[User, Depends(current_user)]):
    # user = session.get(User, todo.user_id)
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")
    
    new_todo = Todo(title=todo.title, user_id=current_user.id)
    session.add(new_todo)
    session.commit()
    session.refresh(new_todo)
    print("Todo adding", new_todo)

    return new_todo

# ************     ***********    LOGIN USER    ***********     ***********     **********

@app.post("/token", response_model=Token)
async def login_user(form_data:Annotated[OAuth2PasswordRequestForm, Depends()],
                session:Session= Depends(get_session)):
    user = authenticate_user(session=session, username=form_data.username, password=form_data.password)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expiry_time=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


    #************     ***********     GET ALL TODOS OF CURRENT USER ***********     ***********     **********
    

@app.get('/todos/', response_model=list[Todo])
def get_all(current_user:Annotated[User, Depends(current_user)],
                  session: Annotated[Session, Depends(get_session)]):
    
    
    todos = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()

    if todos:
        return todos
    else:
        raise HTTPException(status_code=404, detail="No Task found")

    #   ************     ***********     GET SINGLE TO DO OF CURRENT USER ***********     ***********     **********
@app.get("/todos/{id}", response_model=Todo)
async def get_single_task(id: int, 
                          session: Annotated[Session, Depends(get_session)],
                          current_user:Annotated[User, Depends(current_user)]):
    user_todos = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
    matched_todo = next((todo for todo in user_todos if todo.id == id), None)

    if matched_todo:
        return matched_todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
    

    #   ************     ***********     UPDATE SINGLE TO DO OF CURRENT USER ***********     ***********     **********

@app.patch("/todos/{id}", response_model=Todo)
async def update_todo(id: int, 
                      todo: TodoUpdate,
                      session: Annotated[Session, Depends(get_session)],
                      current_user:Annotated[User, Depends(current_user)]):
    user_todos = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
    update_todo = next((todo for todo in user_todos if todo.id == id), None)
    if update_todo:
        update_todo.title = todo.title
        session.add(update_todo)
        session.commit()
        session.refresh(update_todo)
        return update_todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
    

    #   ************     ***********     PUT SINGLE TO DO OF CURRENT USER ***********     ***********     **********        
    

@app.put("/todos/{id}", response_model=Todo)
async def update_todo(id: int, 
                      todo: TodoUpdate,
                      session: Annotated[Session, Depends(get_session)],
                      current_user:Annotated[User, Depends(current_user)]):
    user_todos = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
    update_todo = next((todo for todo in user_todos if todo.id == id), None)
    if update_todo:
        update_todo.title = todo.title
        session.add(update_todo)
        session.commit()
        session.refresh(update_todo)
        return update_todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
    

    #   ************     ***********     DELETE SINGLE TO DO OF CURRENT USER ***********     ***********     **********

@app.delete("/todos/{id}", response_model=Todo)
async def delete_todo(id: int, 
                      session: Annotated[Session, Depends(get_session)],
                      current_user:Annotated[User, Depends(current_user)]):
    user_todos = session.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
    delete_todo = next((todo for todo in user_todos if todo.id == id), None)
    if delete_todo:
        session.delete(delete_todo)
        session.commit()
        return delete_todo
    else:
        raise HTTPException(status_code=404, detail="Todo not found")