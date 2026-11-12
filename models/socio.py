# Define la tabla de Socios y los esquemas para registrar o editar socios
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.prestamo import Prestamo


# Campos basicos de un socio
class SocioBase(SQLModel):
    nombre: str
    email: str = Field(unique=True, index=True)
    activo: bool = Field(default=True)


# Tabla en la base de datos
class Socio(SocioBase, table=True):
    __tablename__ = "socios"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relacion 1 a N: un socio puede tener varios prestamos pedidos
    prestamos: List["Prestamo"] = Relationship(back_populates="socio")


# Datos que recibimos para registrar un nuevo socio
class SocioCrear(SQLModel):
    nombre: str
    email: str
    activo: bool = True


# Datos que recibimos si se quiere modificar un socio existente
class SocioActualizar(SQLModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    activo: Optional[bool] = None


# Formato de respuesta para devolver un socio
class SocioRespuesta(SocioBase):
    id: int
