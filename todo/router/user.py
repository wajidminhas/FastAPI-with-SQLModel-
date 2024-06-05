

from sqlmodel import Session
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException
from todo.auth import get_user_from_db, hash_password, oauth_scheme
from todo.db import get_session
from todo.model import Register_User, User


user_router: APIRouter = APIRouter(
    prefix="/user",  # ���由前��
    tags=["user"],  # ��������
    responses={404: {"description": "Not found"}}  # ������
)

@user_router.get("/")
async def read_user():
    return {"Message" : "Welcome to Todo App user Interface"}


@user_router.get("/register_user")
async def register_user(new_user: Annotated[Register_User, Depends()],
                        session:Annotated[Session, Depends(get_session)]):
    db_user = get_user_from_db(session, new_user.name,new_user.email)
    if db_user:
        HTTPException(status_code=409, detail= {"Error": "User already exists"})

    user = User(name=new_user.name,
                email=new_user.email,
                password = hash_password(new_user.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    print("User", user)
    return {"Message": f"User {user.name} created successfully"}


@user_router.get("/profile")
async def user_profile(current_user:Annotated[User, Depends(oauth_scheme)]):
    return {"user": "Hello user"}

