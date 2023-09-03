from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from sqlalchemy.sql import func

from sqlite import schemas
from sqlite.enums import DepartmentsEnum, DesignationsEnum
from sqlite.database import Base, engine

Base.metadata.create_all(bind=engine)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    department = Column(Enum(DepartmentsEnum), nullable=False)
    designation = Column(Enum(DesignationsEnum), nullable=False)

    created_at = Column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    def update(self, user: schemas.UserCreateOrUpdate, **kwargs):
        self.full_name = user.full_name
        self.email = user.email
        self.is_admin = user.is_admin
        self.department = user.department
        self.designation = user.designation
