from fastapi import APIRouter, Depends

from app.database.models import UserModel
from app.dependencies.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)



@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: UserModel = Depends(get_current_user),
):
    return current_user

from app.dependencies.auth import get_current_admin


@router.get("/admin-test")
async def admin_test(
    current_admin: UserModel = Depends(get_current_admin),
):
    return {
        "message": "You are admin",
        "user_id": current_admin.id,
    }