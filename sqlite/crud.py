from sqlalchemy.orm import Session
from sqlite import models, schemas

from datetime import datetime


def get_all_users(db: Session):
    return db.query(models.UserModel).all()


def get_all_admin_users(db: Session):
    return db.query(models.UserModel).filter(models.UserModel.is_admin == True).all()


def get_all_staff_members(db: Session):
    return db.query(models.UserModel).filter(models.UserModel.is_admin == False).all()


def get_user_by_id(user_id: int, db: Session):
    return db.query(models.UserModel).filter(models.UserModel.id == user_id).first()


def get_user_by_email(user_email: str, db: Session):
    return (
        db.query(models.UserModel).filter(models.UserModel.email == user_email).first()
    )


def create_user(user: schemas.UserCreateOrUpdate, db: Session):
    db_user = models.UserModel(**user.__dict__)
    db.add(db_user)
    db.commit()
    return db_user


def update_user(
    user: schemas.UserCreateOrUpdate, db_user: models.UserModel, db: Session
):
    db_user.update(user)
    db.commit()
    return db_user


def delete_user(db_user: models.UserModel, db: Session):
    db.delete(db_user)
    db.commit()
    return db_user
