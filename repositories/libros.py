from typing import Optional

from sqlmodel import Session, select

from models.autor import Autor
from models.libro import Libro
from models.libro_autor import LibroAutor
from models.prestamo import Prestamo


def crear(sesion: Session, libro: Libro) -> Libro:
    sesion.add(libro)
    sesion.commit()
    sesion.refresh(libro)
    return libro


def listar(sesion: Session, disponibles: Optional[bool] = None) -> list[Libro]:
    statement = select(Libro)
    if disponibles is True:
        statement = statement.where(Libro.stock > 0)
    return list(sesion.exec(statement).all())


def obtener_por_id(sesion: Session, libro_id: int) -> Optional[Libro]:
    return sesion.get(Libro, libro_id)


def obtener_por_isbn(
    sesion: Session,
    isbn: str,
    excluir_id: Optional[int] = None,
) -> Optional[Libro]:
    statement = select(Libro).where(Libro.isbn == isbn)
    if excluir_id is not None:
        statement = statement.where(Libro.id != excluir_id)
    return sesion.exec(statement).first()


def actualizar(sesion: Session, libro: Libro, cambios: dict) -> Libro:
    for campo, valor in cambios.items():
        setattr(libro, campo, valor)
    sesion.add(libro)
    sesion.commit()
    sesion.refresh(libro)
    return libro


def eliminar(sesion: Session, libro: Libro) -> None:
    prestamos = sesion.exec(
        select(Prestamo).where(Prestamo.libro_id == libro.id)
    ).all()
    for prestamo in prestamos:
        sesion.delete(prestamo)
    sesion.delete(libro)
    sesion.commit()


def obtener_autor_por_id(sesion: Session, autor_id: int) -> Optional[Autor]:
    return sesion.get(Autor, autor_id)


def asociar_autor(sesion: Session, libro: Libro, autor: Autor) -> Libro:
    asociacion = sesion.get(
        LibroAutor,
        (libro.id, autor.id),
    )
    if asociacion is None:
        sesion.add(LibroAutor(libro_id=libro.id, autor_id=autor.id))
        sesion.commit()
        sesion.refresh(libro)
    return libro
