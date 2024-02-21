from sqlalchemy.orm import Session
from sqlalchemy import and_

from sqlite import models
from sqlite.enums import AttendanceEnum


def get_attendance_by_schedule_instance_id(schedule_instance_id: int, db: Session):
    """Get attendance by schedule instances id from the database"""
    return (
        db.query(models.AttendanceModel)
        .filter(models.AttendanceModel.schedule_instance_id == schedule_instance_id)
        .first()
    )


def get_attendance_by_id(attendance_id: int, db: Session):
    """Get attendance by id from the database"""
    return (
        db.query(models.AttendanceModel)
        .filter(models.AttendanceModel.id == attendance_id)
        .first()
    )


def get_all_attendance_by_schedule_ids(schedule_ids: list[int], db: Session):
    """Get attendance for a particular duration from the database"""
    return (
        db.query(models.AttendanceModel)
        .filter(models.AttendanceModel.schedule_instance_id.in_(schedule_ids))
        .all()
    )


def create_attendance(
    schedule_instance_id: int,
    attendance_status: AttendanceEnum,
    db: Session,
):
    """Create a new attendance in the database"""
    db_attendance = models.AttendanceModel(
        schedule_instance_id=schedule_instance_id, attendance_status=attendance_status
    )
    db.add(db_attendance)
    db.commit()

    return db_attendance
