from datetime import datetime, date

from sqlalchemy.orm import Session
from sqlalchemy import and_

from sqlite import models

# from sqlite.schemas import ScheduleInstanceCreateOrUpdateClass


def get_all_schedule_instances(db: Session):
    """Get all schedule instances (reoccurring and non-reoccurring) (reoccurring and non-reoccurring)from the database"""
    return db.query(models.ScheduleInstanceModel)


def get_all_schedule_instances_by_date(date: date, db: Session):
    """Get all schedule instances (reoccurring and non-reoccurring) by date from the database"""
    return db.query(models.ScheduleInstanceModel).filter(
        models.ScheduleInstanceModel.date == date
    )


def get_all_schedule_instance_by_date_range_and_user_id(
    start_date: date, end_date: date, user_id: int, db: Session
):
    """Get all schedule instances (reoccurring and non-reoccurring) for a given date range by user id from the database"""
    return db.query(models.ScheduleInstanceModel).filter(
        and_(
            models.ScheduleInstanceModel.date >= start_date,
            models.ScheduleInstanceModel.date <= end_date,
            models.ScheduleInstanceModel.staff_member_id == user_id,
        )
    )


def get_today_schedule_instances(db: Session):
    """Get all schedule instances (reoccurring and non-reoccurring) for the current date (today) from the database"""
    now = datetime.utcnow()
    return db.query(models.ScheduleInstanceModel).filter(
        models.ScheduleInstanceModel.date == now.date()
    )


def get_today_schedule_instances_by_user_id(user_id: int, db: Session):
    """Get all schedule instances (reoccurring and non-reoccurring) for the current date (today) by user id from the database"""
    now = datetime.utcnow()
    return db.query(models.ScheduleInstanceModel).filter(
        and_(
            models.ScheduleInstanceModel.staff_member_id == user_id,
            models.ScheduleInstanceModel.date == now.date(),
        )
    )


def get_schedule_instance_by_id(schedule_instance_id: int, db: Session):
    """Get a single schedule instance (reoccurring or non-reoccurring) by id from the database"""
    return (
        db.query(models.ScheduleInstanceModel)
        .filter(models.ScheduleInstanceModel.id == schedule_instance_id)
        .first()
    )


# def create_schedule_instance(
#     schedule_instance: ScheduleInstanceCreateOrUpdateClass, db: Session
# ):
#     """Create a new schedule instance (reoccurring or non-reoccurring) in the database"""
#     db_schedule_instance = models.ScheduleInstanceModel(**schedule_instance.__dict__)
#     db.add(db_schedule_instance)
#     db.commit()

#     return db_schedule_instance


# def update_schedule_instance(
#     schedule_instance: ScheduleInstanceCreateOrUpdateClass,
#     db_schedule_instance: models.ScheduleInstanceModel,
#     db: Session,
# ):
#     """Update a schedule instance (reoccurring or non-reoccurring) in the database"""
#     db_schedule_instance.update(schedule_instance=schedule_instance)
#     db.commit()

#     return db_schedule_instance


# def delete_schedule_instance(
#     db_schedule_instance: models.ScheduleInstanceModel, db: Session
# ):
#     """Delete a schedule instance (reoccurring or non-reoccurring) from the database"""
#     db.delete(db_schedule_instance)
#     db.commit()

#     return {"detail": "Deleted successfully"}
