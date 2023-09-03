from pydantic import BaseModel
from datetime import datetime

from sqlite.enums import DepartmentsEnum, DesignationsEnum


class UserBase(BaseModel):
    full_name: str
    email: str
    is_admin: bool = False
    department: DepartmentsEnum = DepartmentsEnum.SOFTWATE
    designation: DesignationsEnum = DesignationsEnum.ASSISTANT_PROFESSOR


class UserCreateOrUpdate(UserBase):
    pass


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        orm_mode = True
