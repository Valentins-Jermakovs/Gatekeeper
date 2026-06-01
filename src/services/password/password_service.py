# =====================================================
#                       imports
# =====================================================
from pwdlib import PasswordHash
# =====================================================


# =====================================================
#                   Biznesa loģika
# =====================================================

# Inicializē paroļu šifrētāju
password_hash = PasswordHash.recommended()

# Metode paroles hešošanai
async def hash_password(password: str) -> str:
    return password_hash.hash(password)

# Metode paroļu verifikācijai
async def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)