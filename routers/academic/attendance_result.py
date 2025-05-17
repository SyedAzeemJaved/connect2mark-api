from fastapi import Depends, APIRouter

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlite.dependency import get_db_session
from sqlalchemy.orm import Session

from sqlite.crud import attendance
from sqlite.crud.schedule_instances import (
    get_all_schedule_instance_by_date_range_and_user_id,
)

from sqlite.schemas import AttendanceResult, AttendanceSearchClass, User

from utils.auth import get_current_user, should_be_academic_user
from utils.responses import common_responses

router = APIRouter(
    prefix="/academic/attendance-result",
    tags=["academic - attendance-result"],
    dependencies=[
        Depends(should_be_academic_user),
    ],
    responses=common_responses(),
)


@router.post(
    "",
    response_model=Page[AttendanceResult],
)
async def get_attendance_for_duration(
    data: AttendanceSearchClass,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    schedule_instances = get_all_schedule_instance_by_date_range_and_user_id(
        start_date=data.start_date,
        end_date=data.end_date,
        user_id=current_user.id,
        db=db,
    )
    attendance_list = attendance.get_all_attendance_by_schedule_ids(
        schedule_ids=[x.id for x in schedule_instances], db=db
    )
    attendance_dict = {obj.schedule_instance.id: obj for obj in attendance_list}

    return paginate(
        schedule_instances,
        transformer=lambda x: [
            AttendanceResult(
                schedule_instance=item,
                attendance_status=(
                    attendance_dict.get(item.id).attendance_status
                    if attendance_dict.get(item.id)
                    else None
                ),
                created_at_in_utc=(
                    attendance_dict.get(item.id).created_at_in_utc
                    if attendance_dict.get(item.id)
                    else None
                ),
            )
            for item in x
        ],
    )
