
#  Define la tabla de Prestamos en la base de datos y los esquemas
#  para pedir un prestamo y para registrar su devolucion.


from datetime import date
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from models.socio import Socio
    from models.libro import Libro

# Campos basicos del prestamo
class PrestamoBase(SQLModel):
    socio_id: int = Field(foreign_key="socios.id")
    libro_id: int = Field(foreign_key="libros.id")
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: Optional[date] = None
    multa: float = Field(default=0.0)


# Tabla de prestamos en la base de datos
class Prestamo(PrestamoBase, table=True):
    __tablename__ = "prestamos"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relaciones N a 1: cada prestamo pertenece a un socio y a un libro
    socio: Optional["Socio"] = Relationship(back_populates="prestamos")
    libro: Optional["Libro"] = Relationship(back_populates="prestamos")


# Lo que envia el cliente para pedir un prestamo.
# La fecha_prestamo es opcional: si no la manda, usamos la fecha de hoy.
class PrestamoCrear(SQLModel):
    socio_id: int
    libro_id: int
    fecha_prestamo: Optional[date] = None


# Lo que envia el cliente al devolver el libro.
# La fecha_devolucion es opcional: si no la manda, usamos la fecha de hoy.
# Esto es muy util para pruebas donde queremos simular que pasaron dias de atraso.
class PrestamoDevolucion(SQLModel):
    fecha_devolucion: Optional[date] = None


# Formato de respuesta con los datos completos del prestamo
class PrestamoRespuesta(PrestamoBase):
    id: int
