# Importē bibliotēkas
from sqlmodel import Field, SQLModel

# Roles (lomas) modelis
class Role(SQLModel, table=True):

    # Tabulas nosaukums
    __tablename__ = "roles"

    # Lomas identifikators
    id: int = Field(default=None, primary_key=True)

    # Lomas nosaukums
    name: str = Field(
        max_length=50,
        unique=True,
        index=True
    )

    # Lomas apraksts
    description: str = Field(max_length=256)