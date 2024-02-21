from fastapi import Depends, APIRouter

from sqlite.database import get_db
from sqlalchemy.orm import Session

import sqlite.crud.stats as crud

from sqlite.schemas import (
    StatsBaseClass,
)
from utils.auth import user_should_be_admin
from utils.responses import common_responses

router = APIRouter(
    prefix="/stats",
    tags=["admin - stats"],
    dependencies=[
        Depends(user_should_be_admin),
    ],
    responses=common_responses(),
)


@router.get(
    "",
    summary="Get a stats for the dashboard",
    response_model=StatsBaseClass,
)
async def get_all_stats(db: Session = Depends(get_db)):
    return crud.get_all_stats(db=db)
