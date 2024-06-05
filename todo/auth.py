
from datetime import datetime, timedelta, timezone
from fastapi import Depends
from sqlmodel import Session, select
from typing_extensions import Annotated
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from todo.db import get_session
from todo.model import  User
from fastapi import HTTPException
from jose import jwt, JWTError


#  TO PROTECT ROUTE WE USE THIS SHCEMA 
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/token")


pwd_context = CryptContext(schemes=["bcrypt"])

# function for password authentication 



def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password, hash_password):
    return pwd_context.verify(password, hash_password)

def get_user_from_db(session : Annotated[Session, Depends(get_session)], 
                     name : str,
                     email : str):
    statement = select(User).where(User.name == name)
    user = session.exec(statement).first()
    if not user:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        if user:
            return user
        
    return user

# function to authenticate user to login 

def authenticate_user(session: Annotated[Session, Depends(get_session)],
                       email: str,
                       password: str,
                       name:str):
    db_user = get_user_from_db(session, email=email, name=name)
    if not db_user:
        return False
    if not verify_password(password=password, hash_password=db_user.password):
        return False
    return db_user


# ACCESS TOKEN GENERATED AND FORMING 

SECRET_KEY = "9ee8d60fdefe9ddf7decea9c0e5a3041733ffe9ef0850999604e681fa15e6fa7"
ALGORITHM = "HS256"
EXPIRY_TIME = 30

def create_access_token(data:dict, expiry_time:timedelta | None):
    data_to_encode = data.copy()
    if expiry_time:
        expire = datetime.now(timezone.utc) + expiry_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    data_to_encode.update( {"exp": expire})
    encode_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt