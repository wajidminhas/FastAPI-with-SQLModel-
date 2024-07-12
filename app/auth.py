
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends
from sqlmodel import Session, select
from typing import Annotated
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from .db import get_session
from .model import  TokenData, User
from fastapi import HTTPException, status
from jose import jwt, JWTError


SECRET_KEY = "587f1ae2e458645e1f7dec6823f5cf67963398700edfedccfe21241fb5279629"
ALGORITHM = "HS256"
EXPIRY_TIME = 30

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
                           email: str):
    statement = select(User).where(User.username == username)
    ser = session.exec(statement).first()
    if not user:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        if user:
            return user
    return user

    



#**********************  AUTHENTICATE USER  **************

def authenticate_user(session:Annotated[Session, Depends(get_session)],
                      username, password, email):
    db_user = get_user_from_db(session=session, username=username, email= email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password (password=password, hash_password=db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    return db_user
    


#**********************  GENERATE JWT TOKEN  **************

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

    #      **********************    **************

def current_user(token: Annotated[str, Depends(oauth_scheme)],
                 session: Annotated[Session, Depends(get_session)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user_from_db(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user




