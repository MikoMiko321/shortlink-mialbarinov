from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    login: str = Field(min_length=3, max_length=15, pattern="^[a-zA-Z0-9]+$")

    password: str = Field(min_length=6, max_length=64)


class UserLogin(BaseModel):
    login: str
    password: str
