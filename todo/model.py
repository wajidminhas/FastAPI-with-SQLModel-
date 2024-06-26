
from fastapi import Form
from typing import Annotated, List
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Relationship, SQLModel, Field
from typing import Optional








  

class Todo(SQLModel, table=True):
    __tablename__ = "todo"
    id: int = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    is_completed: bool = Field(default=False)
    user_id: int = Field(default=None, foreign_key="user.id")

 # ***********     ***********     ***********     ***********     ***********     ********** 

    
class User(SQLModel, table=True):
    __tablename__ = "user"
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
        

 # ***********     ***********     ***********     ***********     ***********     ********** 


        
        # for user credential 
        # add dependency    poetry add python-multipart

class Register_User(BaseModel):
            name : Annotated[
                str,
                Form()
            ]
            password : Annotated[
                str,
                Form()
            ]
            email : Annotated[
                str,
                Form()
            ]

 # ***********     ***********     ***********     ***********     ***********     ********** 

class Token(BaseModel):
       access_token : str
       toke_type : str

class TokenData(BaseModel):
       name : str

