from fastapi import Depends, status, APIRouter, HTTPException


from sqlite.dependency import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite.schemas import TemporaryClass
from sqlite.crud.temporary import get_roboflow_status, flip_roboflow_status


router = APIRouter(
    prefix="/temporary",
    tags=["temporary"],
)


@router.get(
    "",
    summary="Get Roboflow model detection status",
    response_model=TemporaryClass,
)
async def fetch_roboflow_status(
    db: AsyncSession = Depends(get_db_session),
):
    result = await get_roboflow_status(db=db)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
        )

    return {"status": result.status, "id": result.id}


@router.post(
    "",
    summary="Update Roboflow model detection status",
    response_model=TemporaryClass,
)
async def update_roboflow_status(
    db: AsyncSession = Depends(get_db_session),
):
    db_temporary = await get_roboflow_status(db=db)

    if not db_temporary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
        )

    return await flip_roboflow_status(db_temporary=db_temporary, db=db)
