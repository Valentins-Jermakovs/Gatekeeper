# =====================================================
#                       imports
# =====================================================
from sqlmodel import Field, SQLModel
# =====================================================

# Role model
class Role(SQLModel, table=True):

    # Table name
    __tablename__ = "roles"

    # Role id
    id: int = Field(default=None, primary_key=True)

    # Role name
    name: str = Field(
        max_length=50,
        unique=True,
        index=True
    )

    # Role description
    description: str = Field(max_length=256)