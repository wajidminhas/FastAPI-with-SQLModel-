

from sqlmodel import Session
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.auth import current_user, get_user_from_db, hash_password
from app.db import get_session
from app.model import Register_User, User


user_router: APIRouter = APIRouter(
    prefix="/user",  # ���由前��
    tags=["user"],  # ��������
    responses={404: {"description": "Not found"}}  # ������
)

@user_router.get("/")
async def read_user():
    return {"Message" : "Welcome to Todo App user Interface"}

#   for user to register we have to made a model of register user that take data in form 

@user_router.get("/register_user")
async def register_user(new_user : Annotated[Register_User, Depends()],
                        session : Annotated[Session, Depends(get_session)]):
    db_user = get_user_from_db(session, new_user.username, new_user.email)
    if db_user:
        HTTPException(status_code=409, detail="Email is already registerd")

    user = User(username= new_user.username, 
                email=new_user.email,
                password= hash_password(new_user.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"Message" : f"user {user.username} has successfully created"}

    # ****** ********* GET USER FROM DATABASE     ***** **********

@user_router.get("/get_user/{id}")
async def get_user(id : int, session : Annotated[Session, Depends(get_session)]):
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



# delete user from db

@user_router.delete("/delete_user")
async def delete_user(id : int, session : Annotated[Session, Depends(get_session)]):
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"Message" : f"user {user.username} has successfully deleted"}
    

@user_router.get("/profile")
async def user_profile(current_user : Annotated[User, Depends(current_user)]):
    return current_user

