from models import User
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from schemas import UserResponse

async def get_user_info(
    user_id: int,
    user_roles: list,
    db: AsyncSession
) -> UserResponse:
    
    # Get current user from DB

    result = await db.exec(
        select(User).where(User.id == user_id)
    )

    user = result.first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Create user response
    user = UserResponse(
        username=user.username,
        email=user.email,
        roles=user_roles,
        created_at=user.created_at,
        active=user.active
    )

    return user

