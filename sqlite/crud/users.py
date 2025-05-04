from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from sqlite import models
from sqlite.schemas import (
    UserCreateClass,
    UserUpdateClass,
    UserPasswordUpdateClass,
)
from sqlite.enums import DepartmentsEnum, DesignationsEnum

from utils.password import get_password_hash


def get_all_admin_users(db: Session):
    """Get all admin users from the database"""
    return (
        db.query(models.UserModel)
        .filter(models.UserModel.is_admin.is_(True))
        .options(joinedload(models.UserModel.additional_details))
    )


def get_all_academic_users(only_students: bool, db: Session):
    """Get all academic users from the database"""
    return (
        db.query(models.UserModel)
        .filter(
            models.UserModel.is_admin.is_(False),
            models.UserModel.is_student == only_students,
        )
        .options(joinedload(models.UserModel.additional_details))
    )


def get_user_by_id(user_id: int, db: Session):
    """Get a single user by id from the database"""
    return (
        db.query(models.UserModel)
        .filter(models.UserModel.id == user_id)
        .options(joinedload(models.UserModel.additional_details))
        .first()
    )


def get_user_by_email(user_email: str, db: Session):
    """Get a single user by email from the database"""
    return (
        db.query(models.UserModel)
        .filter(models.UserModel.email == user_email)
        .options(joinedload(models.UserModel.additional_details))
        .first()
    )


def get_user_by_phone(user_phone: str, db: Session):
    """Get a single user by phone from the database"""
    return (
        db.query(models.UserModel)
        .join(models.UserModel.additional_details)
        .filter(models.UserAdditionalDetailModel.phone == user_phone)
        .options(joinedload(models.UserModel.additional_details))
        .first()
    )


def create_user(user: UserCreateClass, db: Session):
    (
        """Create a new user, with or without it's additional details in"""
        + """the database"""
    )
    user.password = get_password_hash(user.password)
    db_user = models.UserModel(**user.__dict__)

    if not user.is_admin:
        db_user.additional_details = models.UserAdditionalDetailModel(
            phone=None,
            department=DepartmentsEnum.NOT_SPECIFIED,
            designation=DesignationsEnum.NOT_SPECIFIED,
        )
    db.add(db_user)
    db.commit()

    return db_user


def update_user(user: UserUpdateClass, db_user: models.UserModel, db: Session):
    """Update a user, along with it's additional details in the database"""
    db_user.update(user)
    if db_user.additional_details:
        db_user.additional_details.update(user)
    # Need to manually update updated_at_in_utc
    # Else if only UserAdditionalDetailModel model is updated,
    #  updated_at_in_utc will not trigger
    db_user.updated_at_in_utc = datetime.now(tz=timezone.utc)
    db.commit()

    return db_user


def update_user_password(
    new_password: UserPasswordUpdateClass,
    db_user: models.UserModel,
    db: Session,
):
    """Update a user's password on the database"""
    new_password.new_password = get_password_hash(
        password=new_password.new_password
    )
    db_user.update_password(new_password=new_password.new_password)
    db.commit()

    return db_user


def delete_user(db_user: models.UserModel, db: Session):
    """Delete a user from the database"""
    db.delete(db_user)
    # UserAssociationDetails is on cascade, it will be deleted automatically
    db.commit()

    return {"detail": "Deleted successfully"}
