from datetime import datetime, date

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

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

from utils.date_utils import (
    return_day_of_week_name,
)


def get_all_schedules(db: Session):
    """Get all schedules (reoccurring and non-reoccurring) from the database"""
    return db.query(models.ScheduleModel)


def get_all_schedules_by_date(date: date, db: Session):
    """Get all schedules (reoccurring and non-reoccurring) by date from the database"""
    return db.query(models.ScheduleModel).filter(models.ScheduleModel.date == date)


def get_all_schedules_by_day(day: DaysEnum, db: Session):
    """Get all schedules (reoccurring and non-reoccurring) by day from the database"""
    return db.query(models.ScheduleModel).filter(models.ScheduleModel.day == day)


def get_today_schedules(db: Session):
    """Get all schedules (reoccurring and non-reoccurring) for the current day or date (today) from the database"""
    now = datetime.utcnow()
    return db.query(models.ScheduleModel).filter(
        or_(
            and_(
                models.ScheduleModel.is_reoccurring == True,
                models.ScheduleModel.date == None,
                models.ScheduleModel.day == return_day_of_week_name(date=now),
            ),
            and_(
                models.ScheduleModel.is_reoccurring == False,
                models.ScheduleModel.date == now.date(),
                models.ScheduleModel.day == return_day_of_week_name(date=now),
            ),
        )
    )


def get_all_schedules_by_user_id(user_id: int, db: Session):
    """ "Get all schedules (reoccurring) and non-reoccurring for a particular user"""
    return db.query(models.ScheduleModel).filter(
        models.ScheduleModel.staff_member_id == user_id
    )


def get_reoccurring_schedule(schedule: ScheduleReoccurringSearchClass, db: Session):
    """Get a single reoccurring schedule from the database"""
    return (
        db.query(models.ScheduleModel)
        .filter(
            and_(
                models.ScheduleModel.start_time_in_utc == schedule.start_time_in_utc,
                models.ScheduleModel.end_time_in_utc == schedule.end_time_in_utc,
                models.ScheduleModel.staff_member_id == schedule.staff_member_id,
                models.ScheduleModel.location_id == schedule.location_id,
                models.ScheduleModel.day == schedule.day,
            )
        )
        .first()
    )


def get_non_reoccurring_schedule(
    schedule: ScheduleNonReoccurringSearchClass, db: Session
):
    """Get a single non-reoccurring schedule from the database"""
    return (
        db.query(models.ScheduleModel)
        .filter(
            and_(
                models.ScheduleModel.start_time_in_utc == schedule.start_time_in_utc,
                models.ScheduleModel.end_time_in_utc == schedule.end_time_in_utc,
                models.ScheduleModel.staff_member_id == schedule.staff_member_id,
                models.ScheduleModel.location_id == schedule.location_id,
                models.ScheduleModel.date == schedule.date,
            )
        )
        .first()
    )


def get_schedule_by_id(schedule_id: str, db: Session):
    """Get a single schedule (reoccurring or non-reoccurring) by id from the database"""
    return (
        db.query(models.ScheduleModel)
        .filter(models.ScheduleModel.id == schedule_id)
        .first()
    )


def create_schedule(
    schedule: ScheduleReoccurringCreateClass | ScheduleNonReoccurringCreateClass,
    db: Session,
):
    """Create a new schedule (reoccurring or non-reoccurring) in the database"""
    if isinstance(schedule, ScheduleReoccurringCreateClass):
        db_schedule = models.ScheduleModel(
            **schedule.__dict__, is_reoccurring=True, date=None
        )
    else:
        db_schedule = models.ScheduleModel(
            **schedule.__dict__,
            is_reoccurring=False,
            day=return_day_of_week_name(date=schedule.date)
        )
    db.add(db_schedule)
    db.commit()

    return db_schedule


def update_schedule(
    schedule: ScheduleReoccurringUpdateClass | ScheduleNonReoccurringUpdateClass,
    db_schedule: models.ScheduleModel,
    db: Session,
):
    """Update a schedule (reoccurring or non-reoccurring) in the database"""
    if isinstance(schedule, ScheduleReoccurringUpdateClass):
        db_schedule.update_reoccurring(schedule=schedule)
    else:
        db_schedule.update_non_reoccurring(
            schedule=schedule, day=return_day_of_week_name(date=schedule.date)
        )
    db.commit()

    return db_schedule


def delete_schedule(db_schedule: models.ScheduleModel, db: Session):
    """Delete a schedule (reoccurring or non-reoccurring) from the database"""
    db.delete(db_schedule)
    db.commit()

    return {"detail": "Deleted successfully"}
