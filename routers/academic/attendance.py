from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, APIRouter


from sqlite.database import get_db
from sqlalchemy.orm import Session

from sqlite.crud import attendance
from sqlite.crud.schedule_instances import (
    get_schedule_instance_by_id,
)

from sqlite.schemas import Attendance, User
from sqlite.enums import AttendanceEnum

from utils.auth import get_current_user, should_be_academic_user
from utils.responses import common_responses

router = APIRouter(
    prefix="/academic/attendance",
    tags=["academic - attendance"],
    dependencies=[
        Depends(should_be_academic_user),
    ],
    responses=common_responses(),
)


@router.post(
    "/mark/{schedule_instance_id}",
    response_model=Attendance,
)
async def mark_attendance(
    schedule_instance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_schedule_instance = get_schedule_instance_by_id(
        schedule_instance_id=schedule_instance_id, db=db
    )

    if not db_schedule_instance:
        raise HTTPException(
            status_code=403, detail="Schedule instance or class not found"
        )

    if not db_schedule_instance.academic_user_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Can not mark attendance on a schedule instance or class "
            + "that you are not associated with",
        )

    if attendance.get_attendance_by_schedule_instance_id(
        schedule_instance_id=db_schedule_instance.id, db=db
    ):
        raise HTTPException(
            status_code=403, detail="Attendance has already been marked"
        )

    # Getting current datetime
    now = datetime.now(tz=timezone.utc)

    # Date validations
    if not db_schedule_instance.date == now.date():
        raise HTTPException(
            status_code=403,
            detail="Can not mark attendance to this schedule instance or class",
        )

    # Time validations
    if now.time() < db_schedule_instance.start_time_in_utc:
        raise HTTPException(
            status_code=403,
            detail="Can not mark attendance to a schedule instance or class "
            + "before it starts",
        )

    if now.time() > db_schedule_instance.end_time_in_utc:
        raise HTTPException(
            status_code=403,
            detail="Can not mark attendance to a schedule instance or class "
            + "after it ends",
        )

    # Validations complete, user can mark attendance and is PRESENT
    attendance_status = AttendanceEnum.PRESENT

    # Get the current UTC date without the time
    current_utc_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Get start_datetime_utc from start_time_in_utc
    start_datetime_utc = current_utc_date + timedelta(
        hours=db_schedule_instance.start_time_in_utc.hour,
        minutes=db_schedule_instance.start_time_in_utc.minute,
        seconds=db_schedule_instance.start_time_in_utc.second,
    )

    # Get end_datetime_utc from end_time_in_utc
    end_datetime_utc = current_utc_date + timedelta(
        hours=db_schedule_instance.end_time_in_utc.hour,
        minutes=db_schedule_instance.end_time_in_utc.minute,
        seconds=db_schedule_instance.end_time_in_utc.second,
    )

    # Calculate the difference between start_datetime_utc and end_datetime_utc
    time_difference = end_datetime_utc - start_datetime_utc
    # Calculate the midpoint time
    # (50% between start_time_in_utc and end_time_in_utc)
    midpoint_time = start_datetime_utc + time_difference / 2

    # Calculate attendace status
    if midpoint_time <= now:
        attendance_status = AttendanceEnum.LATE

    return attendance.create_attendance(
        schedule_instance_id=schedule_instance_id,
        attendance_status=attendance_status,
        db=db,
    )
