from datetime import datetime, date

from fastapi import Depends, HTTPException, APIRouter

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlite.database import get_db
from sqlalchemy.orm import Session

from sqlite.crud import schedule_instances
from sqlite.crud.users import get_user_by_id
from sqlite.crud.locations import get_location_by_id

from sqlite.schemas import (
    ScheduleInstance,
    ScheduleInstanceUpdateClass,
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


async def should_schedule_instance_be_edited_or_deleted(
    schedule_instance: ScheduleInstance, db: Session
):
    now = datetime.utcnow()
    schedule_instance_dto = datetime(
        year=schedule_instance.date.year,
        month=schedule_instance.date.month,
        day=schedule_instance.date.day,
        hour=schedule_instance.start_time_in_utc.hour,
        minute=schedule_instance.start_time_in_utc.minute,
        second=schedule_instance.start_time_in_utc.second,
    )
    # Check if schedule_instance or class has not started
    if schedule_instance_dto < now:
        raise HTTPException(
            status_code=403,
            detail="You can not edit or delete a class after it has started",
        )
    # No need to check for attendance, as we can only mark attendance after a class has started
    # One a class has started, we can not delete it regardless

    # Check if no attendance has been marked
    # if get_attendance_by_schedule_instance_id(
    #     schedule_instance_id=schedule_instance.id, db=db
    # ):
    #     raise HTTPException(
    #         status_code=403,
    #         detail="You can not edit or delete a class whose attendance has been marked",
    #     )


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


@router.put(
    "/{schedule_instance_id}",
    response_model=ScheduleInstance,
)
async def update_schedule_instance(
    schedule_instance_id: int,
    schedule_instance: ScheduleInstanceUpdateClass,
    db: Session = Depends(get_db),
):
    db_schedule_instance = schedule_instances.get_schedule_instance_by_id(
        schedule_instance_id=schedule_instance_id,
        db=db,
    )
    if db_schedule_instance is None:
        raise HTTPException(status_code=404, detail="Schedule instance not found")
    new_staff_member = get_user_by_id(user_id=schedule_instance.staff_member_id, db=db)
    if not new_staff_member:
        raise HTTPException(status_code=404, detail="User not found")
    if new_staff_member.is_admin:
        raise HTTPException(status_code=403, detail="User should be a staff member")
    if not get_location_by_id(location_id=schedule_instance.location_id, db=db):
        raise HTTPException(status_code=404, detail="Location not found")
    await should_schedule_instance_be_edited_or_deleted(
        schedule_instance=db_schedule_instance, db=db
    )
    return schedule_instances.update_schedule_instance(
        schedule_instance=schedule_instance,
        db_schedule_instance=db_schedule_instance,
        db=db,
    )


@router.delete(
    "/{schedule_instance_id}",
    response_model=CommonResponseClass,
)
async def delete_schedule_instance(
    schedule_instance_id: int, db: Session = Depends(get_db)
):
    db_schedule_instance = schedule_instances.get_schedule_instance_by_id(
        schedule_instance_id=schedule_instance_id, db=db
    )
    if db_schedule_instance is None:
        raise HTTPException(status_code=404, detail="Schedule instance not found")
    await should_schedule_instance_be_edited_or_deleted(
        schedule_instance=db_schedule_instance, db=db
    )
    return schedule_instances.delete_schedule_instance(
        db_schedule_instance=db_schedule_instance, db=db
    )
