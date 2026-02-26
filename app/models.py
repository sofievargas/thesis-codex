from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str

class EntryCreate(BaseModel):
    city: str
    original: str
    target: str
    word: str
    name: str
