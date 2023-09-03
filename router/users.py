from fastapi import Depends, HTTPException, APIRouter

from sqlite.database import get_db
from sqlalchemy.orm import Session

from sqlite import crud
from sqlite.schemas import UserCreateOrUpdate, User


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[User])
async def get_everyone(db: Session = Depends(get_db)):
    return crud.get_all_users(db=db)


@router.get("/admins", response_model=list[User])
async def get_all_admins(db: Session = Depends(get_db)):
    return crud.get_all_admin_users(db=db)


@router.get("/staff", response_model=list[User])
async def get_all_staff_members(db: Session = Depends(get_db)):
    return crud.get_all_staff_members(db=db)


@router.get("/{user_id}", response_model=User)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(user_id=user_id, db=db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/", response_model=User)
async def create_user(user: UserCreateOrUpdate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(user_email=user.email, db=db)
    if db_user is None:
        return crud.create_user(user=user, db=db)
    raise HTTPException(status_code=403, detail="User already exists")


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int, user: UserCreateOrUpdate, db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_id(user_id=user_id, db=db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(user=user, db_user=db_user, db=db)


@router.delete("/{user_id}", response_model=User)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(user_id=user_id, db=db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db_user=db_user, db=db)
