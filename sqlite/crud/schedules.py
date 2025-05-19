from datetime import datetime, date, timezone

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite import models
from sqlite.schemas import (
    ScheduleReoccurringCreateClass,
    ScheduleNonReoccurringCreateClass,
    ScheduleReoccurringUpdateClass,
    ScheduleNonReoccurringUpdateClass,
    # Search
    ScheduleReoccurringSearchClass,
    ScheduleNonReoccurringSearchClass,
)
from sqlite.enums import DaysEnum

from utils.date_utils import return_day_of_week_name


def get_all_schedules_query():
    return select(models.ScheduleModel)


def get_all_schedules_by_date_query(date: date):
    return select(models.ScheduleModel).where(models.ScheduleModel.date == date)


def get_all_schedules_by_day_query(day: DaysEnum):
    return select(models.ScheduleModel).where(models.ScheduleModel.day == day)


def get_today_schedules_query():
    now = datetime.now(tz=timezone.utc)

    return select(models.ScheduleModel).where(
        or_(
            and_(
                models.ScheduleModel.is_reoccurring.is_(True),
                models.ScheduleModel.date.is_(None),
                models.ScheduleModel.day == return_day_of_week_name(date=now),
            ),
            and_(
                ~models.ScheduleModel.is_reoccurring.is_(False),
                models.ScheduleModel.date == now.date(),
                models.ScheduleModel.day == return_day_of_week_name(date=now),
            ),
        )
    )


def get_all_schedules_by_user_id_query(user_id: int):
    # TODO: IMPORTANT
    return (
        select(models.ScheduleModel)
        .join(models.ScheduleModel.academic_users)
        .where(models.ScheduleModel.academic_users == user_id)
    )


async def get_reoccurring_schedule(
    schedule: ScheduleReoccurringSearchClass, db: AsyncSession
):
    return await db.scalar(
        select(models.ScheduleModel)
        .join(
            models.UserModel,
            onclause=models.UserModel.id == models.ScheduleModel.teacher_id,
        )
        .where(
            and_(
                models.ScheduleModel.start_time_in_utc
                == schedule.start_time_in_utc,
                models.ScheduleModel.end_time_in_utc
                == schedule.end_time_in_utc,
                models.UserModel.id == schedule.teacher_id,
                models.ScheduleModel.location_id == schedule.location_id,
                models.ScheduleModel.day == schedule.day,
            )
        )
    )


async def get_non_reoccurring_schedule(
    schedule: ScheduleNonReoccurringSearchClass, db: AsyncSession
):
    return await db.scalar(
        select(models.ScheduleModel)
        .join(
            models.UserModel,
            onclause=models.UserModel.id == models.ScheduleModel.teacher_id,
        )
        .where(
            and_(
                models.ScheduleModel.start_time_in_utc
                == schedule.start_time_in_utc,
                models.ScheduleModel.end_time_in_utc
                == schedule.end_time_in_utc,
                models.UserModel.id == schedule.teacher_id,
                models.ScheduleModel.location_id == schedule.location_id,
                models.ScheduleModel.date == schedule.date,
            )
        )
    )


async def get_schedule_by_id(schedule_id: int, db: AsyncSession):
    return await db.scalar(
        select(models.ScheduleModel).where(
            models.ScheduleModel.id == schedule_id
        )
    )


async def create_schedule(
    schedule: (
        ScheduleReoccurringCreateClass | ScheduleNonReoccurringCreateClass
    ),
    db: AsyncSession,
):
    if isinstance(schedule, ScheduleReoccurringCreateClass):
        db_schedule = models.ScheduleModel(
            **schedule.__dict__, is_reoccurring=True, date=None
        )
    else:
        db_schedule = models.ScheduleModel(
            **schedule.__dict__,
            is_reoccurring=False,
            day=return_day_of_week_name(date=schedule.date),
        )

    db.add(db_schedule)

    # db_schedule.academic_users.append(db_academic_user)

    await db.commit()

    await db.refresh(db_schedule)

    return db_schedule


async def update_schedule(
    schedule: (
        ScheduleReoccurringUpdateClass | ScheduleNonReoccurringUpdateClass
    ),
    db_schedule: models.ScheduleModel,
    db: AsyncSession,
):
    if isinstance(schedule, ScheduleReoccurringUpdateClass):
        db_schedule.update_reoccurring(schedule=schedule)
    else:
        db_schedule.update_non_reoccurring(
            schedule=schedule, day=return_day_of_week_name(date=schedule.date)
        )

    await db.commit()

    return db_schedule


async def delete_schedule(db_schedule: models.ScheduleModel, db: AsyncSession):
    await db.delete(db_schedule)

    await db.commit()

    return {"detail": "Deleted successfully"}
