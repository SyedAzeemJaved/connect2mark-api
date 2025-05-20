from datetime import datetime, date, timezone

from fastapi import Depends, status, HTTPException, APIRouter

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlite.dependency import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite.crud import schedule_instances
from sqlite.crud.users import get_user_by_id
from sqlite.crud.locations import get_location_by_id

from sqlite.schemas import (
    ScheduleInstance,
    ScheduleInstanceUpdateClass,
    CommonResponseClass,
)

from utils.auth import should_be_admin_user
from utils.responses import common_responses

router = APIRouter(
    prefix="/admin/schedule-instances",
    tags=["admin - schedule instances or classes"],
    dependencies=[
        Depends(should_be_admin_user),
    ],
    responses=common_responses(),
)


def should_schedule_instance_be_edited_or_deleted(
    schedule_instance: ScheduleInstance, db: AsyncSession
):
    now = datetime.now(tz=timezone.utc)

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
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can not edit or delete a class after it has started",
        )

    # No need to check for attendance, as we can only
    # mark attendance after a class has started
    # One a class has started, we can not delete it regardless

    # Check if no attendance has been marked
    # if get_attendance_by_schedule_instance_id(
    #     schedule_instance_id=schedule_instance.id, db=db
    # ):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You can not edit or delete a class whose attendance
    #  has been marked",
    #     )


@router.get("", response_model=Page[ScheduleInstance])
async def get_all_schedule_instancess(
    db: AsyncSession = Depends(get_db_session),
):
    return await paginate(
        db, schedule_instances.get_all_schedule_instances_query()
    )


@router.get("/date/{date}", response_model=Page[ScheduleInstance])
async def get_all_schedule_instances_by_date(
    date: date, db: AsyncSession = Depends(get_db_session)
):
    return await paginate(
        db,
        schedule_instances.get_all_schedule_instances_by_date_query(date=date),
    )


@router.get(
    "/today",
    summary="Get All Schedules Instances For Today (Current Date)",
    response_model=Page[ScheduleInstance],
)
async def get_all_schedule_instances_for_today(
    db: AsyncSession = Depends(get_db_session),
):
    return await paginate(
        db, schedule_instances.get_today_schedule_instances_query()
    )


@router.get(
    "/today/{academic_user_id}",
    summary="Get All Schedules Instances For An Academic User "
    + "For Today (Current Date)",
    response_model=Page[ScheduleInstance],
)
async def get_all_schedule_instances_for_academic_users_for_today(
    academic_user_id: int, db: AsyncSession = Depends(get_db_session)
):
    db_user = await get_user_by_id(user_id=academic_user_id, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if db_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an academic member",
        )

    return await paginate(
        db,
        schedule_instances.get_today_schedule_instances_by_user_id_query(
            user_id=db_user.id
        ),
    )


@router.get("/{schedule_instance_id}", response_model=ScheduleInstance)
async def get_schedule_instance_by_id(
    schedule_instance_id: int, db: AsyncSession = Depends(get_db_session)
):

    db_schedule_instance = await schedule_instances.get_schedule_instance_by_id(
        schedule_instance_id=schedule_instance_id, db=db
    )

    if db_schedule_instance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule instance not found",
        )

    return db_schedule_instance


@router.put(
    "/{schedule_instance_id}",
    response_model=ScheduleInstance,
)
async def update_schedule_instance(
    schedule_instance_id: int,
    schedule_instance: ScheduleInstanceUpdateClass,
    db: AsyncSession = Depends(get_db_session),
):
    db_schedule_instance = await schedule_instances.get_schedule_instance_by_id(
        schedule_instance_id=schedule_instance_id,
        db=db,
    )

    if db_schedule_instance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule instance not found",
        )

    db_teacher = await get_user_by_id(
        user_id=schedule_instance.teacher_id, db=db
    )

    if not db_teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if db_teacher.is_admin or db_teacher.is_student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User should be a teacher",
        )

    if not await get_location_by_id(
        location_id=schedule_instance.location_id, db=db
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )

    should_schedule_instance_be_edited_or_deleted(
        schedule_instance=db_schedule_instance, db=db
    )

    return await schedule_instances.update_schedule_instance(
        schedule_instance=schedule_instance,
        db_schedule_instance=db_schedule_instance,
        db=db,
    )


@router.delete(
    "/{schedule_instance_id}",
    response_model=CommonResponseClass,
)
async def delete_schedule_instance(
    schedule_instance_id: int, db: AsyncSession = Depends(get_db_session)
):
    db_schedule_instance = await schedule_instances.get_schedule_instance_by_id(
        schedule_instance_id=schedule_instance_id, db=db
    )

    if db_schedule_instance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule instance not found",
        )

    should_schedule_instance_be_edited_or_deleted(
        schedule_instance=db_schedule_instance, db=db
    )

    return await schedule_instances.delete_schedule_instance(
        db_schedule_instance=db_schedule_instance, db=db
    )
