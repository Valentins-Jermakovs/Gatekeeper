# =====================================================
#                       imports
# =====================================================
from sqlmodel import Field, SQLModel
# =====================================================

# User Role model
class UserRoles(SQLModel, table=True):

    # Table name
    __tablename__ = "user_roles"

    # Foreign keys
    user_id: int = Field(foreign_key="users.id", primary_key=True)
    role_id: int = Field(foreign_key="roles.id", primary_key=True)