from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from sqlite import models

from collections import defaultdict


async def get_all_attendance_tracking_by_schedule_instance_id(
    schedule_instance_id: int, db: AsyncSession
):
    result = await db.execute(
        select(models.AttendanceTrackingModel)
        .options(
            joinedload(models.AttendanceTrackingModel.user),
            joinedload(models.AttendanceTrackingModel.schedule_instance),
        )
        .where(
            models.AttendanceTrackingModel.schedule_instance_id
            == schedule_instance_id
        )
    )

    return result.scalars().all()


async def create_attendance_tracking(
    schedule_instance_id: int,
    user_id: int,
    now: datetime,
    db: AsyncSession,
):
    db_attendance_tracking = models.AttendanceTrackingModel(
        schedule_instance_id=schedule_instance_id,
        user_id=user_id,
        created_at_in_utc=now,
    )

    db.add(db_attendance_tracking)

    await db.commit()
    await db.refresh(db_attendance_tracking)

    # Eagerly load nested relationships
    result = await db.execute(
        select(models.AttendanceTrackingModel)
        .options(
            joinedload(models.AttendanceTrackingModel.user),
            joinedload(models.AttendanceTrackingModel.schedule_instance)
            .joinedload(models.ScheduleInstanceModel.teacher)
            .joinedload(models.UserModel.additional_details),
        )
        .where(models.AttendanceTrackingModel.id == db_attendance_tracking.id)
    )
    db_attendance = result.scalar_one()

    return db_attendance


async def get_all_attendance_tracking_result_by_schedule_instance_id(
    schedule_instance_id: int, db: AsyncSession
):
    # Fetch the schedule instance to get class duration
    schedule_instance = await db.get(
        models.ScheduleInstanceModel, schedule_instance_id
    )
    class_duration_ms = None

    if (
        schedule_instance
        and schedule_instance.start_time_in_utc
        and schedule_instance.end_time_in_utc
        and hasattr(schedule_instance, "date")  # Ensure you have a date field
    ):
        start_dt = datetime.combine(
            schedule_instance.date, schedule_instance.start_time_in_utc
        )
        end_dt = datetime.combine(
            schedule_instance.date, schedule_instance.end_time_in_utc
        )
        # If end time is past midnight, adjust date
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        class_duration_ms = (end_dt - start_dt).total_seconds() * 1000
    else:
        class_duration_ms = None

    result = await db.execute(
        select(
            models.AttendanceTrackingModel.user_id,
            models.UserModel.full_name,
            models.UserModel.email,
            models.UserModel.is_student,
            models.AttendanceTrackingModel.created_at_in_utc,
        )
        .join(
            models.UserModel,
            models.AttendanceTrackingModel.user_id == models.UserModel.id,
        )
        .where(
            models.AttendanceTrackingModel.schedule_instance_id
            == schedule_instance_id
        )
        .order_by(
            models.UserModel.email,
            models.AttendanceTrackingModel.created_at_in_utc,
        )
    )
    rows = result.all()

    # Group by user email
    user_data = defaultdict(
        lambda: {
            "user_id": None,
            "full_name": None,
            "email": None,
            "is_student": None,
            "created_at_list": [],
        }
    )

    for user_id, name, email, is_student, created_at in rows:
        data = user_data[email]
        data["user_id"] = user_id
        data["full_name"] = name
        data["email"] = email
        data["is_student"] = is_student
        data["created_at_list"].append(created_at)

    # Prepare summary
    summary = []
    SECONDS_PER_PING = 30

    for email, data in user_data.items():
        created_ats = sorted(
            [dt for dt in data["created_at_list"] if dt is not None]
        )
        num_pings = len(created_ats)
        total_seconds = num_pings * SECONDS_PER_PING
        total_minutes = total_seconds / 60

        # Class duration in minutes
        class_duration_minutes = (
            class_duration_ms / (1000 * 60) if class_duration_ms else None
        )

        percentage = (
            (total_minutes / class_duration_minutes) * 100
            if class_duration_minutes and class_duration_minutes > 0
            else None
        )

        summary.append(
            {
                "user_id": data["user_id"],
                "full_name": data["full_name"],
                "email": data["email"],
                "is_student": data["is_student"],
                "created_at_list": created_ats,
                "first_entry": created_ats[0] if created_ats else None,
                "total_time_in_class_minutes": total_minutes,
                "attendance_percentage": percentage,
            }
        )

    return summary
