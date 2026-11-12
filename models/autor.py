# Define como es la tabla de Autores en la base de datos
# y los datos que se piden para crearlo o actualizarlo.
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from models.libro_autor import LibroAutor

if TYPE_CHECKING:
    from models.libro import Libro


# Modelo base con los campos comunes de un Autor
class AutorBase(SQLModel):
    nombre: str
    nacionalidad: str


# Tabla en la base de datos
class Autor(AutorBase, table=True):
    __tablename__ = "autores"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relacion N a N: un autor puede haber escrito muchos libros.
    # Usamos LibroAutor como tabla intermedia (link_model).
    libros: List["Libro"] = Relationship(back_populates="autores", link_model=LibroAutor)


# Datos que nos envian para crear un autor (no pedimos ID porque lo crea la base de datos)
class AutorCrear(AutorBase):
    pass

# Datos que nos envian para actualizar un autor (pueden venir vacios si no quiere cambiar algo)
class AutorActualizar(SQLModel):
    nombre: Optional[str] = None
    nacionalidad: Optional[str] = None

# Formato de respuesta simple para devolver un autor
class AutorRespuesta(AutorBase):
    id: int
