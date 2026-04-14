import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

from app.api.dependencies import SessionDep, FormDep
from app.schemas import Token
from app.core.security import authenticate_user, create_access_token, InvalidCredentialsException


load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or 15)

router = APIRouter()


# Login and generate JWT token for user
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: FormDep,
    db: SessionDep,
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise InvalidCredentialsException
    token = create_access_token(
        data={"sub": user.username, "id": user.id, "role": user.role},
        expiration_time_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return Token(access_token=token, token_type="bearer")
