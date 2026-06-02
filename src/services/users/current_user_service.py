from models import User
from fastapi import HTTPException
from sqlmodel import select, AsyncSession

async def get_current_user(
    user_id: int,
    user_roles: list,
    db: AsyncSession
):
    result = await db.exec(
        select(User).where(User.id == user_id)
    )

    user = result.first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

