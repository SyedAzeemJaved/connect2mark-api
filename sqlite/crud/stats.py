from sqlalchemy.orm import Session

from sqlite import models
from sqlite.schemas import StatsBaseClass


def get_all_stats(db: Session):
    """Get all stats for the dashboard form the database"""
    staff_count = (
        db.query(models.UserModel).filter(models.UserModel.is_admin == False).count()
    )
    location_count = db.query(models.LocationModel).count()
    schedules_count = db.query(models.ScheduleModel).count()
    schedule_instances_count = db.query(models.ScheduleInstanceModel).count()

    return StatsBaseClass(
        staff_count=staff_count,
        locations_count=location_count,
        schedules_count=schedules_count,
        schedule_instances_count=schedule_instances_count,
    )
