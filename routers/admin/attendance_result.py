from fastapi import Depends, status, HTTPException, APIRouter

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlite.dependency import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite.crud import attendance
from sqlite.crud.users import get_user_by_id
from sqlite.crud.schedule_instances import (
    get_all_schedule_instance_by_date_range_and_user_id_query,
)

from sqlite.schemas import AttendanceResult, AttendanceSearchClass

from utils.auth import should_be_admin_user
from utils.responses import common_responses


router = APIRouter(
    prefix="/admin/attendance-result",
    tags=["admin - attendance-result"],
    dependencies=[
        Depends(should_be_admin_user),
    ],
    responses=common_responses(),
)


@router.get(
    "/{academic_user_id}",
    response_model=Page[AttendanceResult],
)
async def get_attendance_for_duration(
    academic_user_id: int,
    params: AttendanceSearchClass = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    db_user = await get_user_by_id(user_id=academic_user_id, db=db)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if db_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not an academic user",
        )

    schedule_instances_query = (
        get_all_schedule_instance_by_date_range_and_user_id_query(
            start_date=params.start_date,
            end_date=params.end_date,
            user_id=academic_user_id,
            db=db,
        )
    )
    schedule_instances_res = await db.execute(schedule_instances_query)
    schedule_instances_res = schedule_instances_res.fetchall()
    schedule_instances_res = [res[0] for res in schedule_instances_res]

    attendance_list = await db.execute(
        attendance.get_all_attendance_by_schedule_instance_ids_query(
            schedule_ids=[x.id for x in schedule_instances_res]
        )
    )
    result = attendance_list.fetchall()
    converted_result = [res[0] for res in result]

    attendance_dict = {
        obj.schedule_instance.id: obj for obj in converted_result
    }

    return await paginate(
        db,
        schedule_instances_query,
        transformer=lambda x: [
            AttendanceResult(
                schedule_instance=item,
                attendance_status=(
                    attendance_dict.get(item.id).attendance_status
                    if attendance_dict.get(item.id)
                    else None
                ),
                created_at_in_utc=(
                    attendance_dict.get(item.id, {}).created_at_in_utc
                    if attendance_dict.get(item.id)
                    else None
                ),
            )
            for item in x
        ],
    )
