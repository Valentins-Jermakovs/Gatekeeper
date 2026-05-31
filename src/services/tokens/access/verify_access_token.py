# Importē bibliotēkas
from fastapi import HTTPException
from jose import jwt, JWTError, ExpiredSignatureError
from dotenv import load_dotenv
import os

# Nolasa .env faila saturu
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY nav iestatīts .env failā")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Metode access tokena validācijai
async def verify_access_token(token: str) -> dict:
    try:
        # Pārbauda, vai token ir derīgs
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )

        return payload
    
    # Kļūdu apstrāde
    # Ja tokens nav derīgs
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token has expired")
    
    # Ja tokena signatūra nav derīga
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")