# Importē bibliotēkas
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jose import jwt
import os


# =======================================
#               .env
# =======================================

# Nolasa .env faila saturu
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY nav iestatīts .env failā")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "20"))
except ValueError:
    ACCESS_TOKEN_EXPIRE_MINUTES = 20

# =======================================

# Metode access tokena veidošanai
async def create_access_token(
    user_id: int,
    roles: list[str]
) -> str:

    # Kodē tokenā:
    #   * lietotāja identifikatoru
    #   * lomas
    to_encode = {
        "sub": str(user_id),
        "roles": roles
    }

    # Aprēķina, kad tokens beigsies
    expire = datetime.now(timezone.utc) + (
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Tokena papildināšana - laiki
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp())
    })

    # Atgriež tokenu
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)