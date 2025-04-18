from datetime import datetime, date

from fastapi import Depends, HTTPException, APIRouter

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlite.database import get_db
from sqlalchemy.orm import Session

from sqlite.crud import schedule_instances

from sqlite.schemas import (
    ScheduleInstance,
    User,
    CommonResponseClass,
)

from utils.auth import get_current_user, user_should_be_teacher
from utils.responses import common_responses

router = APIRouter(
    prefix="/staff/schedule-instances",
    tags=["staff - schedule instances or classes"],
    dependencies=[
        Depends(user_should_be_teacher),
    ],
    responses=common_responses(),
)


@router.get(
    "/today",
    summary="Get All Schedules Instances For Current User For Today (Current Date)",
    response_model=Page[ScheduleInstance],
)
async def get_all_schedule_instances_for_current_user_for_today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return paginate(
        schedule_instances.get_today_schedule_instances_by_user_id(
            user_id=current_user.id, db=db
        )
    )


# @router.get("/{schedule_instance_id}", response_model=ScheduleInstance)
# async def get_schedule_instance_for_current_user_by_id(
#     schedule_instance_id: int, db: Session = Depends(get_db)
# ):
#     db_schedule_instance = schedule_instances.get_schedule_instance_by_id(
#         schedule_instance_id=schedule_instance_id, db=db
#     )
#     if db_schedule_instance is None:
#         raise HTTPException(status_code=404, detail="Schedule instance not found")
#     return db_schedule_instance
