from datetime import datetime, timezone

from fastapi import Depends, HTTPException, APIRouter

from sqlite.dependency import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite.crud import attendance_tracking
from sqlite.crud.schedule_instances import (
    get_schedule_instance_by_id,
)

from sqlite.schemas import AttendanceTracking, User

from utils.auth import get_current_user, should_be_admin_user
from utils.responses import common_responses

router = APIRouter(
    prefix="/admin/attendance-tracking",
    tags=["admin - attendance-tracking"],
    dependencies=[
        Depends(should_be_admin_user),
    ],
    responses=common_responses(),
)


@router.get(
    "/{schedule_instance_id}",
    # response_model=AttendanceTracking,
)
async def get_all_attendance_tracking_results(
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

    return await attendance_tracking.get_all_attendance_tracking_result_by_schedule_instance_id(
        schedule_instance_id=schedule_instance_id,
        db=db,
    )
