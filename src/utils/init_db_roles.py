# Importē bibliotēkas un modeļus
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models import RoleModel

# Šī utilīta inicializē lomas
async def init_roles(engine):

    # Darbs ar DB, sesijas izveide
    async with AsyncSession(engine) as session:

        # Lomas
        roles = {
            "user": "User can register, login and manage only own data",
            "admin": "Administrator have full system access",
            "manager": "Manager create system content",
        }

        # Pārbaude vai lomas ir inicializētas
        result = await session.exec(select(RoleModel))
        existing_roles = result.all()

        # Ja lomas ir inicializētas -> izlaiž
        if existing_roles:
            return

        # Inicializē lomas
        for role_name, role_description in roles.items():
            session.add(
                RoleModel(
                    name=role_name,
                    description=role_description
                )
            )

        # Saglabā izmaiņas
        await session.commit()