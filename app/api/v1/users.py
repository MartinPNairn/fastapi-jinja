from fastapi import APIRouter, status, HTTPException
from app.models import User
from app.api.dependencies import SessionDep, CurrentUserDep
from app.crud import update_entry, create_entry, DatabaseError
from app.schemas import UpdatePasswordRequest, HashedPassword, UpdatePhoneRequest, UserCreateRequest, UserResponse
from app.core.security import verify_password_hash, create_password_hash

router = APIRouter()


# Create a new user
@router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_create_request: UserCreateRequest, db: SessionDep):
    user_data = user_create_request.model_dump(exclude={"password"})
    new_user = User(**user_data, hashed_password=create_password_hash(user_create_request.password))
    try:
        user_created = create_entry(new_user, db)
    except DatabaseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return user_created


@router.get("/get-user", status_code=status.HTTP_200_OK)
async def get_user(user: CurrentUserDep):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@router.put("/update-password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(user: CurrentUserDep, db: SessionDep, new_data: UpdatePasswordRequest):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not verify_password_hash(new_data.old_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Wrong current password")
    new_hash = create_password_hash(new_data.new_password)
    new_hashed_password = HashedPassword(
        hashed_password=new_hash
    )
    update_entry(user.id, User, new_hashed_password, db)


@router.put("/update-phone", status_code=status.HTTP_204_NO_CONTENT)
async def update_phone(user: CurrentUserDep, db: SessionDep, new_data: UpdatePhoneRequest):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    update_entry(user.id, User, new_data, db)
