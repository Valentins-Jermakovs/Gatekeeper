# =====================================================
#                       imports
# =====================================================
from sqlmodel import Field, SQLModel
# =====================================================

# Lietotāju un lomu savienojuma modelis
class UserRoles(SQLModel, table=True):

    # Tabulas nosaukums
    __tablename__ = "user_roles"

    # Foreign atslēgas
    user_id: int = Field(foreign_key="users.id", primary_key=True)
    role_id: int = Field(foreign_key="roles.id", primary_key=True)