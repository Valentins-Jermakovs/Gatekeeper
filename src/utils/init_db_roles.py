# ====================================================
#                       imports
# ====================================================
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from models import Role
# ====================================================

# ====================================================
#           Roles initialization
# =====================================================

async def init_roles(engine):

    # Session creation
    async with AsyncSession(engine) as session:

        # Roles definitions
        roles = {
            "user": "User can register, login and manage only own data",
            "admin": "Administrator have full system access",
            "manager": "Manager create system content",
            "librarian": "Librarian can manage books"
        }

        # Check if roles are already initialized
        result = await session.exec(select(Role))
        existing_roles = result.all()

        # If roles are already initialized -> exit
        if existing_roles:
            return

        # Else create roles
        for role_name, role_description in roles.items():
            session.add(
                Role(
                    name=role_name,
                    description=role_description
                )
            )

        # Commit
        await session.commit()