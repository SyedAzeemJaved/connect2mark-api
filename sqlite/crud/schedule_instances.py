from datetime import datetime, date, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite import models
from sqlite.schemas import ScheduleInstanceUpdateClass


def get_all_schedule_instances_query():
    return select(models.ScheduleInstanceModel)


def get_all_schedule_instances_by_date_query(date: date):
    return select(models.ScheduleInstanceModel).where(
        models.ScheduleInstanceModel.date == date
    )


async def get_all_schedule_instance_by_date_range_and_user_id(
    start_date: date, end_date: date, user_id: int, db: AsyncSession
):
    return await db.scalars(
        select(models.ScheduleInstanceModel)
        .join(models.ScheduleInstanceModel.academic_users)
        .where(
            and_(
                models.ScheduleInstanceModel.date >= start_date,
                models.ScheduleInstanceModel.date <= end_date,
                models.ScheduleInstanceModel.academic_users.any(
                    models.UserModel.id == user_id
                ),
            )
        )
    )


def get_today_schedule_instances_query():
    now = datetime.now(tz=timezone.utc)

    return select(models.ScheduleInstanceModel).where(
        models.ScheduleInstanceModel.date == now.date()
    )


def get_today_schedule_instances_by_user_id_query(user_id: int):

    now = datetime.now(tz=timezone.utc)

    return (
        select(models.ScheduleInstanceModel)
        .join(models.ScheduleInstanceModel.academic_users)
        .where(
            and_(
                models.ScheduleInstanceModel.academic_users == user_id,
                models.ScheduleInstanceModel.date == now.date(),
            )
        )
    )


async def get_exact_schedule_instance(
    schedule_id: int,
    academic_user_id: int,
    location_id,
    date: date | None,
    start_time_in_utc: datetime,
    end_time_in_utc: datetime,
    db: AsyncSession,
):
    return db.scalar(
        select(models.ScheduleInstanceModel)
        # TODO: IMPORTANT
        .join(models.ScheduleInstanceModel.academic_users).where(
            and_(
                models.ScheduleInstanceModel.schedule_id == schedule_id,
                models.ScheduleInstanceModel.academic_users == academic_user_id,
                models.ScheduleInstanceModel.location_id == location_id,
                models.ScheduleInstanceModel.date == date,
                models.ScheduleInstanceModel.start_time_in_utc
                == start_time_in_utc,
                models.ScheduleInstanceModel.end_time_in_utc == end_time_in_utc,
            )
        )
    )


async def get_schedule_instance_by_id(
    schedule_instance_id: int, db: AsyncSession
):
    return await db.scalar(
        select(models.ScheduleInstanceModel).where(
            models.ScheduleInstanceModel.id == schedule_instance_id
        )
    )


async def update_schedule_instance(
    schedule_instance: ScheduleInstanceUpdateClass,
    db_schedule_instance: models.ScheduleInstanceModel,
    db: AsyncSession,
):
    db_schedule_instance.update(schedule_instance=schedule_instance)

    await db.commit()

    return db_schedule_instance


async def delete_schedule_instance(
    db_schedule_instance: models.ScheduleInstanceModel, db: AsyncSession
):
    await db.delete(db_schedule_instance)

    await db.commit()

    return {"detail": "Deleted successfully"}
