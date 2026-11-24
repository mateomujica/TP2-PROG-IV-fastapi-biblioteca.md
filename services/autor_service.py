from fastapi import HTTPException
from sqlmodel import Session

from models.autor import Autor, AutorActualizar, AutorCrear
from repositories import autores as autor_repository


def crear_autor(sesion: Session, datos: AutorCrear) -> Autor:
    autor = Autor.model_validate(datos)
    return autor_repository.crear(sesion, autor)


def listar_autores(sesion: Session):
    return autor_repository.listar(sesion)


def obtener_autor_por_id(sesion: Session, autor_id: int) -> Autor:
    autor = autor_repository.obtener_por_id(sesion, autor_id)
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return autor


def actualizar_autor(sesion: Session, autor_id: int, datos: AutorActualizar) -> Autor:
    autor = obtener_autor_por_id(sesion, autor_id)
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    cambios = datos.model_dump(exclude_unset=True)
    return autor_repository.actualizar(sesion, autor, cambios)


def eliminar_autor(sesion: Session, autor_id: int):
    autor = obtener_autor_por_id(sesion, autor_id)
    autor_repository.eliminar(sesion, autor)
    return {"mensaje": "Autor eliminado"}