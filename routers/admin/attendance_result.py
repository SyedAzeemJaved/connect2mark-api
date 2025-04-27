from fastapi import Depends, HTTPException, APIRouter

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlite.database import get_db
from sqlalchemy.orm import Session

from sqlite.crud import attendance
from sqlite.crud.users import get_user_by_id
from sqlite.crud.schedule_instances import (
    get_all_schedule_instance_by_date_range_and_user_id,
)

from sqlite.schemas import AttendanceResult, AttendanceSearchClass

from utils.auth import user_should_be_admin
from utils.responses import common_responses

router = APIRouter(
    prefix="/attendance-result",
    tags=["admin - attendance-result"],
    dependencies=[
        Depends(user_should_be_admin),
    ],
    responses=common_responses(),
)


@router.post(
    "/{academic_user_id}",
    response_model=Page[AttendanceResult],
)
async def get_attendance_for_duration(
    academic_user_id: int,
    data: AttendanceSearchClass,
    db: Session = Depends(get_db),
):
    db_user = get_user_by_id(user_id=academic_user_id, db=db)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.is_admin:
        raise HTTPException(status_code=403, detail="User is not an academic user")
    schedule_instances = get_all_schedule_instance_by_date_range_and_user_id(
        start_date=data.start_date,
        end_date=data.end_date,
        user_id=academic_user_id,
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
