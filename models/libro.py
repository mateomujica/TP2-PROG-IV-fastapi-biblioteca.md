#Define la tabla de Libros y los esquemas para crear/editar libros.
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from models.autor import Autor, AutorRespuesta
from models.libro_autor import LibroAutor

if TYPE_CHECKING:
    from models.prestamo import Prestamo


# Campos comunes que tiene cualquier libro
class LibroBase(SQLModel):
    titulo: str
    isbn: str = Field(unique=True, index=True)
    stock: int = Field(default=0, ge=0)  # ge=0 significa que el stock no puede ser negativo
    anio: int


# Tabla en la base de datos
class Libro(LibroBase, table=True):
    __tablename__ = "libros"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relacion N a N: un libro puede tener varios autores
    # Usamos LibroAutor como tabla intermedia (link_model).
    autores: List[Autor] = Relationship(back_populates="libros", link_model=LibroAutor)

    # Relacion 1 a N: un libro puede tener muchos prestamos registrados
    prestamos: List["Prestamo"] = Relationship(back_populates="libro")


# Datos que recibimos para dar de alta un libro
class LibroCrear(LibroBase):
    pass


# Datos que recibimos para actualizar un libro
class LibroActualizar(SQLModel):
    titulo: Optional[str] = None
    isbn: Optional[str] = None
    stock: Optional[int] = None
    anio: Optional[int] = None


# Formato de respuesta que incluye la lista de autores asociados al libro
class LibroRespuesta(LibroBase):
    id: int
    autores: List[AutorRespuesta] = []
