from celery import Celery
from celery import schedules

from datetime import datetime, timezone

from sqlite.dependency import get_db_session
from sqlite.models import ScheduleInstanceModel

from sqlite.crud import schedules
from sqlite.crud.schedule_instances import get_exact_schedule_instance


FILE_NAME = __name__

celery = Celery(
    FILE_NAME,
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)


@celery.task
def create_schedule_instances_or_classes() -> None:
    # TODO: Check iterator logic
    db_generator = get_db_session()
    db = next(db_generator)
    try:
        today_schedules = schedules.get_today_schedules(db=db)
        now = datetime.now(tz=timezone.utc)

        should_commit = False
        for schedule in today_schedules:
            _ = ScheduleInstanceModel(
                schedule_id=schedule.id,
                staff_member_id=schedule.staff_member_id,
                location_id=schedule.location_id,
                date=(
                    now.date()
                    if schedule.is_reoccurring and schedule.date == None
                    else schedule.date
                ),
                start_time_in_utc=schedule.start_time_in_utc,
                end_time_in_utc=schedule.end_time_in_utc,
            )
            if not get_exact_schedule_instance(
                schedule_id=_.schedule_id,
                staff_member_id=_.staff_member_id,
                location_id=_.location_id,
                date=_.date,
                start_time_in_utc=_.start_time_in_utc,
                end_time_in_utc=_.end_time_in_utc,
                db=db,
            ):
                db.add(_)
                if not should_commit:
                    should_commit = True
        if should_commit:
            db.commit()
    except Exception as e:
        print("There seems to be an error")
        print(e)
    finally:
        db.close()


# Schedule the task
celery.conf.beat_schedule = {
    "task-every-30-seconds": {
        "task": f"{FILE_NAME}.create_schedule_instances_or_classes",
        "schedule": 30.0,  # Run every 30 seconds
    },
    # "task-every-day-at-7am": {
    #     "task": f"{FILE_NAME}.create_schedule_instances_or_classes",
    #     "schedule": schedules.crontab(hour=7, minute=0),  # Run every day at 7am,
    # },
}

# celery -A celery_worker.celery worker -B --loglevel=info
