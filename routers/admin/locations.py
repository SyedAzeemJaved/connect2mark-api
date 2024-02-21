from fastapi import Depends, HTTPException, APIRouter

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlite.database import get_db
from sqlalchemy.orm import Session

from sqlite.crud import locations

from sqlite.schemas import (
    LocationCreateOrUpdateClass,
    Location,
    CommonResponseClass,
)

from utils.auth import user_should_be_admin
from utils.responses import common_responses

from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/locations",
    tags=["admin - locations"],
    dependencies=[
        Depends(user_should_be_admin),
    ],
    responses=common_responses(),
)


@router.get("", response_model=Page[Location])
async def get_all_locations(db: Session = Depends(get_db)):
    return paginate(locations.get_all_locations(db=db))


@router.get("/{location_id}", response_model=Location)
async def get_location_by_id(location_id: int, db: Session = Depends(get_db)):
    db_location = locations.get_location_by_id(location_id=location_id, db=db)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return db_location


@router.post(
    "",
    response_model=Location,
)
async def create_location(
    location: LocationCreateOrUpdateClass, db: Session = Depends(get_db)
):
    if locations.get_location(
        bluetooth_address=location.bluetooth_address,
        coordinates=location.coordinates,
        db=db,
    ):
        raise HTTPException(
            status_code=403, detail="Bluetooth address or coordinates already in use"
        )
    return locations.create_location(location=location, db=db)


@router.put(
    "/{location_id}",
    response_model=Location,
)
async def update_location(
    location_id: int,
    location: LocationCreateOrUpdateClass,
    db: Session = Depends(get_db),
):
    db_location = locations.get_location_by_id(
        location_id=location_id,
        db=db,
    )
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return locations.update_location(location=location, db_location=db_location, db=db)


@router.delete(
    "/{location_id}",
    response_model=CommonResponseClass,
)
async def delete_location(location_id: int, db: Session = Depends(get_db)):
    db_location = locations.get_location_by_id(location_id=location_id, db=db)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    try:
        return locations.delete_location(db_location=db_location, db=db)
    except IntegrityError:
        raise HTTPException(
            status_code=403,
            detail="Can not delete a location which has schedules or classes attached to its",
        )
    except:
        raise HTTPException(status_code=500, detail="Unable to delete exception")
