# Define la tabla intermedia para la relacion Muchos a Muchos
# entre Libros y Autores.
from typing import Optional
from sqlmodel import SQLModel, Field


class LibroAutor(SQLModel, table=True):
    __tablename__ = "libro_autores"

    libro_id: Optional[int] = Field(default=None, foreign_key="libros.id", primary_key=True)
    autor_id: Optional[int] = Field(default=None, foreign_key="autores.id", primary_key=True)
