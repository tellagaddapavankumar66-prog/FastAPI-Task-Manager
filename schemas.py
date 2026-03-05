from pydantic import BaseModel
from typing import List, Optional

class TaskBase(BaseModel):
    title: str

class Task(TaskBase):
    id: int
    completed: bool
    class Config:
        from_attributes = True # V2 update idhi

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True