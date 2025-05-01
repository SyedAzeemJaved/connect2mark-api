from typing import Literal

from fastapi import Depends, HTTPException, APIRouter

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlite.database import get_db
from sqlalchemy.orm import Session

from sqlite.crud import users

from sqlite.schemas import (
    UserCreateClass,
    UserUpdateClass,
    UserPasswordUpdateClass,
    User,
    CommonResponseClass,
)

from utils.common import are_object_to_edit_and_other_object_same
from utils.auth import should_be_admin_user
from utils.responses import common_responses

router = APIRouter(
    prefix="/users",
    tags=["admin - users"],
    dependencies=[
        Depends(should_be_admin_user),
    ],
    responses=common_responses(),
)


@router.get("/admins", response_model=Page[User])
async def get_all_admins(db: Session = Depends(get_db)):
    return paginate(users.get_all_admin_users(db=db))


@router.get("/academic", response_model=Page[User])
async def get_all_academic_users(
    only_students: Literal["yes", "no"], db: Session = Depends(get_db)
):
    return paginate(
        users.get_all_academic_users(
            only_students=(only_students == "yes"), db=db
        )
    )


@router.get("/{user_id}", response_model=User)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = users.get_user_by_id(user_id=user_id, db=db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post(
    "",
    response_model=User,
)
async def create_user(user: UserCreateClass, db: Session = Depends(get_db)):
    db_user = users.get_user_by_email(user_email=user.email, db=db)

    if db_user:
        raise HTTPException(status_code=403, detail="User already exists")

    if user.is_admin and user.is_student:
        raise HTTPException(
            status_code=403,
            detail="User can not be admin and student at the same time",
        )

    return users.create_user(user=user, db=db)


@router.put(
    "/{user_id}",
    response_model=User,
)
async def update_user(
    user_id: int, user: UserUpdateClass, db: Session = Depends(get_db)
):
    db_user = users.get_user_by_id(user_id=user_id, db=db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    other_object = users.get_user_by_email(user_email=user.email, db=db)
    if other_object:
        if not are_object_to_edit_and_other_object_same(
            obj_to_edit=db_user,
            other_object_with_same_unique_field=other_object,
        ):
            raise HTTPException(
                status_code=403, detail="User with same email already exists"
            )
    if db_user.is_admin:
        if user.additional_details != None:
            raise HTTPException(
                status_code=403,
                detail="Admins do not need to specify additional details",
            )
    else:
        if user.additional_details == None:
            raise HTTPException(
                status_code=403,
                detail="You need to specify additional details while updating a user",
            )
        if user.additional_details.phone:
            other_object = users.get_user_by_phone(
                user_phone=user.additional_details.phone, db=db
            )
            if other_object:
                if not are_object_to_edit_and_other_object_same(
                    obj_to_edit=db_user,
                    other_object_with_same_unique_field=other_object,
                ):
                    raise HTTPException(
                        status_code=403,
                        detail="This phone number is already in use",
                    )
    return users.update_user(user=user, db_user=db_user, db=db)


@router.patch(
    "/password/{user_id}",
    response_model=User,
)
async def update_user_password(
    user_id: int,
    new_password: UserPasswordUpdateClass,
    db: Session = Depends(get_db),
):
    db_user = users.get_user_by_id(user_id=user_id, db=db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return users.update_user_password(
        new_password=new_password, db_user=db_user, db=db
    )


@router.delete(
    "/{user_id}",
    response_model=CommonResponseClass,
)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = users.get_user_by_id(user_id=user_id, db=db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return users.delete_user(db_user=db_user, db=db)
