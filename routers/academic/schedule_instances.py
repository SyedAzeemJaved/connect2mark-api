from fastapi import Depends, APIRouter

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlite.dependency import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite.crud import schedule_instances

from sqlite.schemas import (
    ScheduleInstance,
    User,
)

from utils.auth import get_current_user, should_be_academic_user
from utils.responses import common_responses

router = APIRouter(
    prefix="/academic/schedule-instances",
    tags=["academic - schedule instances or classes"],
    dependencies=[
        Depends(should_be_academic_user),
    ],
    responses=common_responses(),
)


@router.get(
    "/today",
    summary="Get All Schedules Instances For Current User For "
    + "Today (Current Date)",
    response_model=Page[ScheduleInstance],
)
async def get_all_schedule_instances_for_current_user_for_today(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    return await paginate(
        db,
        schedule_instances.get_today_schedule_instances_by_user_id_query(
            user_id=current_user.id
        ),
    )
