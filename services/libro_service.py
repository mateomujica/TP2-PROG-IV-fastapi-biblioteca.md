from fastapi import HTTPException
from sqlmodel import Session

from models.autor import Autor
from models.libro import Libro, LibroActualizar, LibroCrear
from repositories import libros as libro_repository


def _obtener_libro(sesion: Session, libro_id: int) -> Libro:
    libro = libro_repository.obtener_por_id(sesion, libro_id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro


def crear_libro(sesion: Session, datos: LibroCrear) -> Libro:
    existente = libro_repository.obtener_por_isbn(sesion, datos.isbn)
    if existente is not None:
        raise HTTPException(status_code=409, detail="Ya existe un libro con ese ISBN")

    libro = Libro.model_validate(datos)
    return libro_repository.crear(sesion, libro)


def listar_libros(sesion: Session, disponibles=None):
    return libro_repository.listar(sesion, disponibles)


def obtener_libro_por_id(sesion: Session, libro_id: int) -> Libro:
    return _obtener_libro(sesion, libro_id)


def actualizar_libro(sesion: Session, libro_id: int, datos: LibroActualizar) -> Libro:
    libro = _obtener_libro(sesion, libro_id)
    cambios = datos.model_dump(exclude_unset=True)

    if "isbn" in cambios:
        existente = libro_repository.obtener_por_isbn(
            sesion,
            cambios["isbn"],
            excluir_id=libro_id,
        )
        if existente is not None:
            raise HTTPException(status_code=409, detail="Ya existe un libro con ese ISBN")

    if "stock" in cambios and cambios["stock"] is not None and cambios["stock"] < 0:
        raise HTTPException(status_code=400, detail="El stock no puede ser negativo")

    return libro_repository.actualizar(sesion, libro, cambios)


def eliminar_libro(sesion: Session, libro_id: int):
    libro = _obtener_libro(sesion, libro_id)
    libro_repository.eliminar(sesion, libro)
    return {"mensaje": "Libro eliminado"}


def asociar_autor_a_libro(sesion: Session, libro_id: int, autor_id: int) -> Libro:
    libro = _obtener_libro(sesion, libro_id)
    autor = libro_repository.obtener_autor_por_id(sesion, autor_id)
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    return libro_repository.asociar_autor(sesion, libro, autor)