from datetime import datetime, timezone

from fastapi import Depends, HTTPException, APIRouter

from sqlite.dependency import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite.crud import attendance_tracking
from sqlite.crud.schedule_instances import (
    get_schedule_instance_by_id,
    get_all_academic_user_ids_against_a_schedule_instance,
)

from sqlite.schemas import AttendanceTracking, User

from utils.auth import get_current_user, should_be_academic_user
from utils.responses import common_responses

router = APIRouter(
    prefix="/academic/attendance-tracking",
    tags=["academic - attendance-tracking"],
    dependencies=[
        Depends(should_be_academic_user),
    ],
    responses=common_responses(),
)


@router.post(
    "/mark/{schedule_instance_id}",
    response_model=AttendanceTracking,
)
async def mark_attendance_tracking(
    schedule_instance_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    db_schedule_instance = await get_schedule_instance_by_id(
        schedule_instance_id=schedule_instance_id, db=db
    )

    if not db_schedule_instance:
        raise HTTPException(
            status_code=403, detail="Schedule instance or class not found"
        )

    schedule_instance_user_ids = (
        await get_all_academic_user_ids_against_a_schedule_instance(
            db_schedule_instance=db_schedule_instance, db=db
        )
    )

    if current_user.id not in schedule_instance_user_ids:
        raise HTTPException(
            status_code=403,
            detail="Can not mark attendance on a schedule instance or class "
            + "that you are not associated with",
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

    return await attendance_tracking.create_attendance_tracking(
        schedule_instance_id=schedule_instance_id,
        user_id=current_user.id,
        now=now,
        db=db,
    )
