from fastapi import Depends, status, HTTPException, APIRouter

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlite.dependency import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite.crud import locations

from sqlite.schemas import (
    LocationCreateOrUpdateClass,
    Location,
)

from utils.auth import should_be_admin_user
from utils.responses import common_responses

from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/admin/locations",
    tags=["admin - locations"],
    dependencies=[
        Depends(should_be_admin_user),
    ],
    responses=common_responses(),
)


@router.get("", response_model=Page[Location])
async def get_all_locations(db: AsyncSession = Depends(get_db_session)):
    return await paginate(db, locations.get_all_locations_query())


@router.get("/{location_id}", response_model=Location)
async def get_location_by_id(
    location_id: int, db: AsyncSession = Depends(get_db_session)
):
    db_location = await locations.get_location_by_id(
        location_id=location_id, db=db
    )

    if db_location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )

    return db_location


@router.post(
    "",
    response_model=Location,
    status_code=status.HTTP_201_CREATED,
)
async def create_location(
    location: LocationCreateOrUpdateClass,
    db: AsyncSession = Depends(get_db_session),
):
    if await locations.get_location_by_title(
        location_title=location.title, db=db
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Location with this title already exists",
        )

    if await locations.get_location(
        bluetooth_address=location.bluetooth_address,
        coordinates=location.coordinates,
        db=db,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bluetooth address or coordinates already in use",
        )

    await locations.create_location(location=location, db=db)

    return await locations.get_location_by_bluetooth_address(
        bluetooth_address=location.bluetooth_address, db=db
    )


@router.put(
    "/{location_id}",
    response_model=Location,
)
async def update_location(
    location_id: int,
    location: LocationCreateOrUpdateClass,
    db: AsyncSession = Depends(get_db_session),
):
    db_location = await locations.get_location_by_id(
        location_id=location_id,
        db=db,
    )

    if db_location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )

    return await locations.update_location(
        location=location, db_location=db_location, db=db
    )


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int, db: AsyncSession = Depends(get_db_session)
):
    db_location = await locations.get_location_by_id(
        location_id=location_id, db=db
    )
    if db_location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )

    try:
        await locations.delete_location(db_location=db_location, db=db)
        return {"detail": "Deleted successfully"}
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can not delete a location which has schedules or "
            + "classes attached to its",
        )
    except Exception:
        raise HTTPException(
            status_code=500, detail="Unable to delete exception"
        )
