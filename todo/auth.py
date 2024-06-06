
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends
from sqlmodel import Session, select
from typing_extensions import Annotated
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from todo.db import get_session
from todo.model import  TokenData, User
from fastapi import HTTPException, status
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

def create_access_token(data:dict, exp_time: Optional[timedelta] = None):
    data_to_encode = data.copy()
    if exp_time:
        expire = datetime.now(timezone.utc) + exp_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    data_to_encode.update({"expire time :" : expire.timestamp()})
    jwt_encoded = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return jwt_encoded


def current_user(token:Annotated[str, Depends(oauth_scheme)],
                 session: Annotated[Session, Depends(get_session)]):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str | None = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)
        
    except:
        raise credential_exception
    user = get_user_from_db(session, name=token_data.username, email=None)
    if not user:
        raise credential_exception
    return user

