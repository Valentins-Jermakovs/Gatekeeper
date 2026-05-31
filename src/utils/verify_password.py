# Importē bibliotēkas
from pwdlib import PasswordHash

# Inicializē paroļu šifrētāju
password_hash = PasswordHash.recommended()

# Metode paroļu verifikācijai
async def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)