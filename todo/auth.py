
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends
from sqlmodel import Session, select
from typing import Annotated
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from todo.db import get_session
from todo.model import  TokenData, User
from fastapi import HTTPException, status
from jose import jwt, JWTError


#  TO PROTECT ROUTE WE USE THIS SHCEMA 
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/token")



# to convert password into hashed form we create  this shcema we use passlib[bycrypt] dependency 
pwd_context = CryptContext(schemes=["bcrypt"])


#**********************  to encrypt password  **************
def hash_password(password: str)->str:
    return pwd_context.hash(password)

# **********************  VERFYING PASSWORD OF USER   **************

def verify_password(password, hash_password):
    return pwd_context.verify(password, hash_password)

#**********************  GET USER FROM DATABASE  **************

def get_user_from_db(session: Annotated[Session, Depends(get_session)],
                     username: str,
                     useremail:str ):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        statement = select(User).where(User.email == useremail)
        user = session.exec(statement).first()
        if user:
            return user
    
    return user

#**********************  AUTHENTICATE USER  **************

def authenticate_user(session:Annotated[Session, Depends(get_session)],
                      username, password, email):
    db_user = get_user_from_db(session, username=username,useremail=email )
    if not db_user:
        return False
    if not verify_password (password=password, hash_password=db_user.password):
        return False
    return db_user
    

    #      **********************    **************




