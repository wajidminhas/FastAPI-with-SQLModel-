
from fastapi import Form
from typing import Annotated, List
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Relationship, SQLModel, Field
from typing import Optional








  



 # ***********     ***********     ***********     ***********     ***********     ********** 

    
class User(SQLModel, table=True):
    __tablename__ = "user"
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    todos: List["Todo"] = Relationship(back_populates="user")



class Todo(SQLModel, table=True):
    __tablename__ = "todo"
    id: int = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    is_completed: bool = Field(default=False)
    user_id: int = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="todos")

 # ***********     ***********     ***********     ***********     ***********     ********** 


        
        # for user credential 
        # add dependency    poetry add python-multipart

class Register_User(BaseModel):
            username : Annotated[
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

    # create model for todo creation 

class TodoCreate(BaseModel):
    title: str = Field(index=True, min_length=5, max_length=100)


    # create model for update todos

class TodoUpdate(BaseModel):
    title: str = Field(index=True, min_length=5, max_length=100)
    is_completed: bool