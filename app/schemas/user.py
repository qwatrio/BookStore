from pydantic import BaseModel, EmailStr, ConfigDict

from app.database.models import UserRole


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)