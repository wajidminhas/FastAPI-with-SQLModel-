from passlib.context import CryptContext
from sqlmodel import Session, select
from typing import Annotated
from .db import get_session
from fastapi import Depends, HTTPException, status
from .model import  TokenData, User, Todo
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta


SECRET_KEY = "e22847ac9f2b85343271c3295744e29126e23651eba1e514fc18e7c3251991c1"
ALGORITHM = 'HS256'
EXPIRY_TIME = 59

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/token")

pwd_context = CryptContext(schemes=["bcrypt"])


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def get_user_from_db(session: Annotated[Session, Depends(get_session)],
                     username: str | None = None,
                     email: str | None = None):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    print(user)
    if not user:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        if user:
            return user

    return user


def authenticate_user(username,
                      password,
                      session: Annotated[Session, Depends(get_session)]):
    db_user = get_user_from_db(session=session,  username=username)
    print(f""" authenticate {db_user} """)
    if not db_user:
        return False
    if not verify_password(password, hashed_password=db_user.password):
        return False
    return db_user


def create_access_token(data: dict, expiry_time: timedelta | None):
    data_to_encode = data.copy()
    if expiry_time:
        expire = datetime.now(timezone.utc) + expiry_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=55)
    data_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def current_user(token: Annotated[str, Depends(oauth_scheme)],
                 session: Annotated[Session, Depends(get_session)]):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token, Please login again",
        headers={"www-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username: str | None = payload.get("sub")

        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)

    except JWTError:
        raise credential_exception
    user = get_user_from_db(session, username=token_data.username)
    if not user:
        raise credential_exception
    return user


# def create_refresh_token(data: dict, expiry_time: timedelta | None):
#     data_to_encode = data.copy()
#     if expiry_time:
#         expire = datetime.now(timezone.utc) + expiry_time
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=15)
#     data_to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(
#         data_to_encode, SECRET_KEY, algorithm=ALGORITHYM, )
#     return encoded_jwt


# def validate_refresh_token(token: str,
#                            session: Annotated[Session, Depends(get_session)]):

#     credential_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid token, Please login again",
#         headers={"www-Authenticate": "Bearer"}
#     )

#     try:
#         payload = jwt.decode(token, SECRET_KEY, ALGORITHYM)
#         email: str | None = payload.get("sub")
#         if email is None:
#             raise credential_exception
#         token_data = RefreshTokenData(email=email)

#     except:
#         raise JWTError
#     user = get_user_from_db(session, email=token_data.email)
#     if not user:
#         raise credential_exception
#     return user