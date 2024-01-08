from datetime import datetime, date

from fastapi import Depends, HTTPException, APIRouter

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlite.database import get_db
from sqlalchemy.orm import Session

from sqlite.crud import schedule_instances
from sqlite.crud.users import get_user_by_id

from sqlite.schemas import (
    ScheduleInstance,
    CommonResponseClass,
)

from utils.auth import user_should_be_admin
from utils.responses import common_responses

router = APIRouter(
    prefix="/schedule-instances",
    tags=["admin - schedule instances or classes"],
    dependencies=[
        Depends(user_should_be_admin),
    ],
    responses=common_responses(),
)


@router.get("", response_model=Page[ScheduleInstance])
async def get_all_schedule_instancess(db: Session = Depends(get_db)):
    return paginate(schedule_instances.get_all_schedule_instances(db=db))


@router.get("/date/{date}", response_model=Page[ScheduleInstance])
async def get_all_schedule_instances_by_date(date: date, db: Session = Depends(get_db)):
    return paginate(
        schedule_instances.get_all_schedule_instances_by_date(date=date, db=db)
    )


@router.get(
    "/today",
    summary="Get All Schedules Instances For Today (Current Date)",
    response_model=Page[ScheduleInstance],
)
async def get_all_schedule_instances_for_today(db: Session = Depends(get_db)):
    return paginate(schedule_instances.get_today_schedule_instances(db=db))


@router.get(
    "/today/{staff_member_id}",
    summary="Get All Schedules Instances For A Staff Member For Today (Current Date)",
    response_model=Page[ScheduleInstance],
)
async def get_all_schedule_instances_for_staff_member_for_today(
    staff_member_id: int, db: Session = Depends(get_db)
):
    db_user = get_user_by_id(user_id=staff_member_id, db=db)
    if not db_user:
        raise HTTPException(status_code=403, detail="User not found")
    if db_user.is_admin:
        raise HTTPException(status_code=403, detail="User is not a staff member")
    return paginate(
        schedule_instances.get_today_schedule_instances_by_user_id(
            user_id=db_user.id, db=db
        )
    )


@router.get("/{schedule_instance_id}", response_model=ScheduleInstance)
async def get_schedule_instance_by_id(
    schedule_instance_id: int, db: Session = Depends(get_db)
):
    db_schedule_instance = schedule_instances.get_schedule_instance_by_id(
        schedule_instance_id=schedule_instance_id, db=db
    )
    if db_schedule_instance is None:
        raise HTTPException(status_code=404, detail="Schedule instance not found")
    return db_schedule_instance
