# =========================================================================
#                                imports
# =========================================================================
# Bibliotēkas:
from fastapi import Request
from authlib.integrations.starlette_client import OAuth
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException
# Shēmas:
from schemas import (
    LoginRequest, 
    RegistrationRequest,
    TokenResponse, 
)
# Servisi
import services.password.password_service as password_service
import services.tokens.token_service as token_service
# Modeļi
from models import User, Role, UserRoles, RefreshToken
# =========================================================================


# =========================================================================
#                               Biznesa loģika
# =========================================================================


# ============================ Google ======================================
async def google_auth_callback(
    oauth: OAuth,
    db: AsyncSession,
    request: Request
) -> TokenResponse:

    # Iegūst tokenu no Google
    token = await oauth.google.authorize_access_token(request)
    user_info = token["userinfo"]

    email = user_info["email"]
    google_id = user_info["sub"]


    # Meklē lietotaju pēc google_id
    result = await db.exec(
        select(User).where(User.google_id == google_id)
    )
    user = result.first()

    if user and not user.active:
        raise HTTPException(status_code=401, detail="User is inactive")

    
    # Ja nav -> meklē pēc email
    if not user:
        result = await db.exec(
            select(User).where(User.email == email)
        )
        user = result.first()

        if user and not user.active:
            raise HTTPException(status_code=401, detail="User is inactive")

    # Lietotāja izveide vai atjaunošana
    if user:
        user.google_id = google_id
        user.auth_provider = "google"
    else:
        user = User(
            email=email,
            google_id=google_id,
            auth_provider="google",
            username=None,
            password_hash=None,
            active=True,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        # ===== Jaunā lietotāja 'user' lomas piešķiršana =====

        result = await db.exec(
            select(Role).where(Role.name == "user")
        )

        role = result.first()

        if role:
            db.add(
                UserRoles(
                    user_id=user.id, 
                    role_id=role.id
                )
            )
            await db.commit()

    # Ja lietotājs nav atjaunots, izlaiž
    await db.commit()
    await db.refresh(user)

    # Veco tokenu dzēšana
    result = await db.exec(
        select(RefreshToken).where(RefreshToken.user_id == user.id)
    )
    old_tokens = result.all()

    for t in old_tokens:
        await db.delete(t)

    await db.commit()


    # Toķenu ģenerācija
    refresh_token_value = await token_service.create_refresh_token()

    await token_service.save_refresh_token(
        refresh_token=refresh_token_value,
        user_id=user.id,
        db=db
    )

    # ===== Access tokena izveide =====

    # Lietotāja lomu ieguve
    result = await db.exec(
        select(Role.name)
        .join(UserRoles, UserRoles.role_id == Role.id)
        .where(UserRoles.user_id == user.id)
    )

    roles = result.all()

    access_token = await token_service.create_access_token(user_id=user.id, roles=roles)

    print("Access token:", access_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_value
    )


# ================= Lietotāja reģistrācijas metode ========================
async def register_user(
    db: AsyncSession, 
    user_registration_data: RegistrationRequest
) -> TokenResponse:
    # ===== Lietotāja eksistences pārbaude =====

    # Normalizējam lietotāja datus
    user_registration_data.username = user_registration_data.username.lower()
    user_registration_data.email = user_registration_data.email.lower()

    # Pārbaude uz lietotāja eksistenci DB
    result = await db.exec(
        select(User).where(User.username == user_registration_data.username)
    )
    
    existing_user = result.first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    

    # Pārbaude uz e-pastu DB
    result = await db.exec( 
        select(User).where(User.email == user_registration_data.email)
    )

    existing_email = result.first()

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    

    # ===== Jaunā lietotāja reģistrācija =====
    
    new_user = User(
        username=user_registration_data.username,
        email=user_registration_data.email,
        password_hash=await password_service.hash_password(user_registration_data.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # ===== Jaunā lietotāja 'user' lomas piešķiršana =====

    result = await db.exec(
        select(Role).where(Role.name == "user")
    )

    role = result.first()

    if role:
        db.add(
            UserRoles(
                user_id=new_user.id, 
                role_id=role.id
            )
        )
        await db.commit()

    
    # ===== Tokenu izveide =====

    access_token = await token_service.create_access_token(
        user_id=new_user.id, 
        roles=["user"]
    )

    refresh_token = await token_service.create_refresh_token()
    await token_service.save_refresh_token(refresh_token, new_user.id, db)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


# ========================= Lietotāja login ================================
async def authenticate_user(
    db: AsyncSession,
    data: LoginRequest
) -> TokenResponse:
    
    # Normalizē lietotājvārdu
    username = data.username.lower()

    # Meklē lietotāju
    result = await db.exec(
        select(User).where(User.username == username)
    )

    user = result.first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Paroles pārbaude
    if not password_service.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Pārbauda, vai lietotājs nav bloķēts
    if not user.active:
        raise HTTPException(status_code=403, detail="User is blocked")
    
    # ===== Tokenu rotācija (refresh) =====

    # Dzēš veco refresh tokenu
    await token_service.delete_refresh_token_by_user_id(user_id=user.id, db=db)

    # Jaunā tokena izveide
    new_refresh_token = await token_service.create_refresh_token()
    await token_service.save_refresh_token(
        refresh_token=new_refresh_token, 
        user_id=user.id, db=db
    )

    # ===== Access tokena izveide =====

    # Lietotāja lomu ieguve
    result = await db.exec(
        select(Role.name)
        .join(UserRoles, UserRoles.role_id == Role.id)
        .where(UserRoles.user_id == user.id)
    )

    roles = result.all()

    access_token = await token_service.create_access_token(user_id=user.id, roles=roles)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


# ========================= Lietotāja logout =================================
async def logout_user(
    db: AsyncSession,
    refresh_token: str,
) -> dict:
    
    # Dzēšam refresh tokenu no DB
    await token_service.delete_refresh_token(
        refresh_token=refresh_token, 
        db=db
    )

    return {
        "msg": "Logout successful"
    }