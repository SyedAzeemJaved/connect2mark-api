from celery import Celery
from celery import schedules

from datetime import datetime

from sqlite.database import get_db

from sqlite.models import ScheduleInstanceModel

from sqlite.crud import schedules


FILE_NAME = __name__

celery = Celery(
    FILE_NAME,
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)


@celery.task
def create_schedule_instances_or_classes() -> None:
    db_generator = get_db()
    db = next(db_generator)
    try:
        today_schedules = schedules.get_today_schedules(db=db)
        for s in today_schedules:
            print(s)

        now = datetime.utcnow()

        print("This is now: ", now)

        schedule_instances_list = list()
        for schedule in today_schedules:
            schedule_instances_list.append(
                ScheduleInstanceModel(
                    schedule_id=schedule.id,
                    staff_member_id=schedule.staff_member_id,
                    location_id=schedule.location_id,
                    date=now.date()
                    if schedule.is_reoccurring and schedule.date == None
                    else schedule.date,
                    start_time_in_utc=schedule.start_time_in_utc,
                    end_time_in_utc=schedule.end_time_in_utc,
                )
            )
        if schedule_instances_list:
            db.add_all(schedule_instances_list)
            db.commit()
            print("Commited successfully")
    except Exception as e:
        print(" --- I am in Exception ---")
        print(e)
    finally:
        db.close()


# Schedule the task
celery.conf.beat_schedule = {
    "task-every-20-seconds": {
        "task": f"{FILE_NAME}.create_schedule_instances_or_classes",
        "schedule": 10.0,  # Run every 10 seconds
    },
    # "task-every-day-at-7am": {
    #     "task": f"{FILE_NAME}.create_schedule_instances_or_classes",
    #     "schedule": schedules.crontab(hour=7, minute=0),  # Run every day at 7am,
    # },
}

# celery -A celery_worker.celery worker -B --loglevel=info
