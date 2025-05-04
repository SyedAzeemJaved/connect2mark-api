from datetime import datetime, date, timezone

from sqlalchemy.orm import Session
from sqlalchemy import and_

from sqlite import models
from sqlite.schemas import ScheduleInstanceUpdateClass


def get_all_schedule_instances(db: Session):
    """Get all schedule instances from the database"""
    return db.query(models.ScheduleInstanceModel)


def get_all_schedule_instances_by_date(date: date, db: Session):
    """Get all schedule instances by date from the database"""
    return db.query(models.ScheduleInstanceModel).filter(
        models.ScheduleInstanceModel.date == date
    )


def get_all_schedule_instance_by_date_range_and_user_id(
    start_date: date, end_date: date, user_id: int, db: Session
):
    (
        """Get all schedule instances for a given date range by user id from """
        + """the database"""
    )
    return db.query(models.ScheduleInstanceModel).filter(
        and_(
            models.ScheduleInstanceModel.date >= start_date,
            models.ScheduleInstanceModel.date <= end_date,
            models.ScheduleInstanceModel.academic_user_id == user_id,
        )
    )


def get_today_schedule_instances(db: Session):
    (
        """Get all schedule instances for the current date (today) from """
        + """the database"""
    )
    now = datetime.now(tz=timezone.utc)
    return db.query(models.ScheduleInstanceModel).filter(
        models.ScheduleInstanceModel.date == now.date()
    )


def get_today_schedule_instances_by_user_id(user_id: int, db: Session):
    (
        """Get all schedule instances for the current date (today) by user """
        + """id from the database"""
    )
    now = datetime.now(tz=timezone.utc)
    return db.query(models.ScheduleInstanceModel).filter(
        and_(
            models.ScheduleInstanceModel.academic_user_id == user_id,
            models.ScheduleInstanceModel.date == now.date(),
        )
    )


def get_exact_schedule_instance(
    schedule_id: int,
    academic_user_id: int,
    location_id,
    date: date | None,
    start_time_in_utc: datetime,
    end_time_in_utc: datetime,
    db: Session,
):
    """Get exactly matching schedule instance from the database"""
    return (
        db.query(models.ScheduleInstanceModel)
        .filter(
            and_(
                models.ScheduleInstanceModel.schedule_id == schedule_id,
                models.ScheduleInstanceModel.academic_user_id
                == academic_user_id,
                models.ScheduleInstanceModel.location_id == location_id,
                models.ScheduleInstanceModel.date == date,
                models.ScheduleInstanceModel.start_time_in_utc
                == start_time_in_utc,
                models.ScheduleInstanceModel.end_time_in_utc == end_time_in_utc,
            )
        )
        .first()
    )


def get_schedule_instance_by_id(schedule_instance_id: int, db: Session):
    """Get a single schedule instance by id from the database"""
    return (
        db.query(models.ScheduleInstanceModel)
        .filter(models.ScheduleInstanceModel.id == schedule_instance_id)
        .first()
    )


def update_schedule_instance(
    schedule_instance: ScheduleInstanceUpdateClass,
    db_schedule_instance: models.ScheduleInstanceModel,
    db: Session,
):
    """Update a schedule instance in the database"""
    db_schedule_instance.update(schedule_instance=schedule_instance)
    db.commit()

    return db_schedule_instance


def delete_schedule_instance(
    db_schedule_instance: models.ScheduleInstanceModel, db: Session
):
    """Delete a schedule instance from the database"""
    db.delete(db_schedule_instance)
    db.commit()

    return {"detail": "Deleted successfully"}
