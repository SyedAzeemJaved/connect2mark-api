from datetime import datetime, date, time, timezone

from fastapi import Depends, HTTPException, APIRouter

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlite.dependency import get_db_session
from sqlalchemy.orm import Session

from sqlite.crud import schedules
from sqlite.crud.users import get_user_by_id
from sqlite.crud.locations import get_location_by_id

from sqlite.schemas import (
    ScheduleReoccurringCreateClass,
    ScheduleNonReoccurringCreateClass,
    ScheduleReoccurringUpdateClass,
    ScheduleNonReoccurringUpdateClass,
    Schedule,
    CommonResponseClass,
    # Search
    ScheduleReoccurringSearchClass,
    ScheduleNonReoccurringSearchClass,
)
from sqlite.enums import DaysEnum

from utils.auth import should_be_admin_user
from utils.responses import common_responses

router = APIRouter(
    prefix="/schedules",
    tags=["admin - schedules"],
    dependencies=[
        Depends(should_be_admin_user),
    ],
    responses=common_responses(),
)


def validate_schedule(
    schedule: (
        ScheduleReoccurringCreateClass
        | ScheduleNonReoccurringCreateClass
        | ScheduleReoccurringUpdateClass
        | ScheduleNonReoccurringUpdateClass
    ),
):
    # Check if start_time_in_utc is less than end_time_in_utc
    if schedule.start_time_in_utc >= schedule.end_time_in_utc:
        raise HTTPException(
            status_code=403, detail="Start time should be less than end time"
        )
    # Check if end_time_in_utc is not greater than 11:30PM
    if schedule.end_time_in_utc > time(
        23, 30, 0, tzinfo=schedule.end_time_in_utc.tzinfo
    ):
        raise HTTPException(
            status_code=403,
            detail="End time should not be greater than 11:30PM",
        )
    # Checks for non-reoccurring schedules
    if isinstance(
        schedule,
        ScheduleNonReoccurringCreateClass | ScheduleNonReoccurringUpdateClass,
    ):
        # Should not be in past
        if schedule.date <= datetime.now(tz=timezone.utc).date():
            raise HTTPException(
                status_code=403,
                detail="Date should not be today or in the past",
            )


@router.get("", response_model=Page[Schedule])
async def get_all_schedules(db: Session = Depends(get_db_session)):
    return paginate(schedules.get_all_schedules(db=db))


@router.get("/date/{date}", response_model=Page[Schedule])
async def get_all_schedules_by_date(
    date: date, db: Session = Depends(get_db_session)
):
    return paginate(schedules.get_all_schedules_by_date(date=date, db=db))


@router.get("/day/{day}", response_model=Page[Schedule])
async def get_all_schedules_by_day(
    day: DaysEnum, db: Session = Depends(get_db_session)
):
    return paginate(schedules.get_all_schedules_by_day(day=day, db=db))


@router.get(
    "/today",
    summary="Get All Schedules For Today By Both Current Day And Date",
    response_model=Page[Schedule],
)
async def get_all_schedules_for_today(
    db: Session = Depends(get_db_session),
):
    return paginate(schedules.get_today_schedules(db=db))


@router.get("/academic/{academic_user_id}", response_model=Page[Schedule])
async def get_all_schedules_for_academic_users(
    academic_user_id: int, db: Session = Depends(get_db_session)
):
    db_user = get_user_by_id(user_id=academic_user_id, db=db)

    if not db_user:
        raise HTTPException(status_code=403, detail="User not found")

    if db_user.is_admin:
        raise HTTPException(
            status_code=403, detail="User is not an academic user"
        )

    return paginate(
        schedules.get_all_schedules_by_user_id(user_id=academic_user_id, db=db)
    )


@router.get("/{schedule_id}", response_model=Schedule)
async def get_schedule_by_id(
    schedule_id: int, db: Session = Depends(get_db_session)
):
    db_schedule = schedules.get_schedule_by_id(schedule_id=schedule_id, db=db)

    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return db_schedule


@router.post(
    "/reoccurring",
    response_model=Schedule,
)
async def create_reoccuring_schedule(
    schedule: ScheduleReoccurringCreateClass,
    db: Session = Depends(get_db_session),
):
    db_academic_user = get_user_by_id(user_id=schedule.academic_user_id, db=db)

    if not db_academic_user or db_academic_user.is_admin:
        raise HTTPException(
            status_code=403, detail="Academic user does not exist"
        )

    if not get_location_by_id(location_id=schedule.location_id, db=db):
        raise HTTPException(status_code=403, detail="Location does not exist")

    # Check if reoccurring schedule already exists
    if schedules.get_reoccurring_schedule(
        schedule=ScheduleReoccurringSearchClass(**schedule.__dict__), db=db
    ):
        raise HTTPException(status_code=403, detail="Schedule already exists")

    validate_schedule(schedule=schedule)

    return schedules.create_schedule(
        schedule=schedule, db_academic_user=db_academic_user, db=db
    )


@router.post(
    "/non-reoccurring",
    response_model=Schedule,
)
async def create_non_reoccuring_schedule(
    schedule: ScheduleNonReoccurringCreateClass,
    db: Session = Depends(get_db_session),
):
    db_academic_user = get_user_by_id(user_id=schedule.academic_user_id, db=db)

    if not db_academic_user or db_academic_user.is_admin:
        raise HTTPException(
            status_code=403, detail="Academic user does not exist"
        )

    if not get_location_by_id(location_id=schedule.location_id, db=db):
        raise HTTPException(status_code=403, detail="Location does not exist")

    # Check if non-reoccurring schedule already exists
    if schedules.get_non_reoccurring_schedule(
        schedule=ScheduleNonReoccurringSearchClass(**schedule.__dict__),
        db=db,
    ):
        raise HTTPException(status_code=403, detail="Schedule already exists")

    validate_schedule(schedule=schedule)
    return schedules.create_schedule(
        schedule=schedule, db_academic_user=db_academic_user, db=db
    )


@router.put(
    "/reoccurring/{schedule_id}",
    response_model=Schedule,
)
async def update_reoccurring_schedule(
    schedule_id: int,
    schedule: ScheduleReoccurringUpdateClass,
    db: Session = Depends(get_db_session),
):
    db_schedule = schedules.get_schedule_by_id(
        schedule_id=schedule_id,
        db=db,
    )

    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")

    if not db_schedule.is_reoccurring:
        raise HTTPException(
            status_code=403,
            detail="Schedule you are trying to update is not reoccurring",
        )

    # TODO
    # You also need to perform check if schedule exists validations here
    validate_schedule(schedule=schedule)

    return schedules.update_schedule(
        schedule=schedule, db_schedule=db_schedule, db=db
    )


@router.put(
    "/non-reoccurring/{schedule_id}",
    response_model=Schedule,
)
async def update_non_reoccurring_schedule(
    schedule_id: int,
    schedule: ScheduleNonReoccurringUpdateClass,
    db: Session = Depends(get_db_session),
):
    db_schedule = schedules.get_schedule_by_id(
        schedule_id=schedule_id,
        db=db,
    )

    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")

    if db_schedule.is_reoccurring:
        raise HTTPException(
            status_code=403,
            detail="Schedule you are trying update is not non-reoccurring",
        )

    # TODO
    # You also need to perform check if schedule exists validations here
    validate_schedule(schedule=schedule)

    return schedules.update_schedule(
        schedule=schedule, db_schedule=db_schedule, db=db
    )


@router.delete(
    "/{schedule_id}",
    response_model=CommonResponseClass,
)
async def delete_schedule(
    schedule_id: int, db: Session = Depends(get_db_session)
):
    db_schedule = schedules.get_schedule_by_id(schedule_id=schedule_id, db=db)

    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return schedules.delete_schedule(db_schedule=db_schedule, db=db)
