# Bibliotēku importi
from sqlmodel.ext.asyncio.session import AsyncSession
from src.services.tokens.refresh.refresh_token import delete_refresh_token


# Metode priekš logout
async def logout(
    db: AsyncSession,
    refresh_token: str,
) -> dict:
    
    # Dzēšam refresh tokenu no DB
    await delete_refresh_token(
        refresh_token=refresh_token, 
        db=db
    )

    return {
        "msg": "Logout successful"
    }