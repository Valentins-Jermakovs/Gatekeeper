# Importē bibliotēkas
from pwdlib import PasswordHash

# Inicializē paroļu šifrētāju
password_hash = PasswordHash.recommended()

# Metode paroles hešošanai
async def hash_password(password: str) -> str:
    return password_hash.hash(password)