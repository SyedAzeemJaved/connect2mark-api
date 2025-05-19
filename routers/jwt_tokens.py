from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm

from datetime import timedelta

from sqlite.dependency import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

from secret import secret

from sqlite.crud.passwords import authenticate_user

from sqlite.schemas import Token
from utils.jwt_tokens import create_access_token


router = APIRouter(
    prefix="/token",
    tags=["auth"],
)


@router.post("", summary="Generate a new access token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    user = await authenticate_user(
        email=form_data.username, password=form_data.password, db=db
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=secret.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
        key=secret.SECRET_KEY,
        algorithm=secret.ALGORITHM,
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user}
