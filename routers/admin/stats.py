from fastapi import Depends, APIRouter

from sqlite.dependency import get_db_session
from sqlalchemy.orm import Session

import sqlite.crud.stats as crud

from sqlite.schemas import (
    StatsBaseClass,
)
from utils.auth import should_be_admin_user
from utils.responses import common_responses

router = APIRouter(
    prefix="/stats",
    tags=["admin - stats"],
    dependencies=[
        Depends(should_be_admin_user),
    ],
    responses=common_responses(),
)


@router.get(
    "",
    summary="Get a stats for the dashboard",
    response_model=StatsBaseClass,
)
async def get_all_stats(db: Session = Depends(get_db_session)):
    return crud.get_all_stats(db=db)
