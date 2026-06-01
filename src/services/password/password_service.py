# =====================================================
#                       imports
# =====================================================
from pwdlib import PasswordHash
# =====================================================


# =====================================================
#                   Business logic
# =====================================================

# Initialize password hasher (argon2)
password_hash = PasswordHash.recommended()

# Function for password hashing
async def hash_password(password: str) -> str:
    return password_hash.hash(password)

# Function for password verification
async def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)