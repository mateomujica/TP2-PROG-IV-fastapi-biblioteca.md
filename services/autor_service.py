#  Logica para crear, consultar, modificar y eliminar autores.
from typing import List
from fastapi import HTTPException, status
from sqlmodel import Session, select

from models.autor import Autor, AutorCrear, AutorActualizar


def crear_autor(sesion: Session, datos: AutorCrear) -> Autor:
    """
    QUE HACE:
        Crea un nuevo autor en la base de datos.
    QUE RECIBE:
        - sesion: conexion activa.
        - datos: nombre y nacionalidad.
    QUE DEVUELVE:
        El autor creado.
    """
    nuevo_autor = Autor(
        nombre=datos.nombre,
        nacionalidad=datos.nacionalidad
    )
    sesion.add(nuevo_autor)
    sesion.commit()
    sesion.refresh(nuevo_autor)
    return nuevo_autor


def listar_autores(sesion: Session) -> List[Autor]:
    """
    QUE HACE:
        Devuelve la lista completa de autores.
    QUE RECIBE:
        - sesion: conexion activa.
    QUE DEVUELVE:
        Lista de autores.
    """
    consulta = select(Autor)
    return sesion.exec(consulta).all()


def obtener_autor_por_id(sesion: Session, autor_id: int) -> Autor:
    """
    QUE HACE:
        Busca un autor por su ID.
    QUE RECIBE:
        - sesion: conexion activa.
        - autor_id: ID del autor a buscar.
    QUE DEVUELVE:
        El autor encontrado.
    """
    autor = sesion.get(Autor, autor_id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado"
        )
    return autor


def actualizar_autor(sesion: Session, autor_id: int, datos: AutorActualizar) -> Autor:
    """
    QUE HACE:
        Modifica los datos de un autor existente.
    QUE RECIBE:
        - sesion: conexion activa.
        - autor_id: ID del autor a modificar.
        - datos: campos a actualizar (nombre, nacionalidad).
    QUE DEVUELVE:
        El autor actualizado.
    """
    autor = obtener_autor_por_id(sesion, autor_id)

    if datos.nombre is not None:
        autor.nombre = datos.nombre
    if datos.nacionalidad is not None:
        autor.nacionalidad = datos.nacionalidad

    sesion.add(autor)
    sesion.commit()
    sesion.refresh(autor)
    return autor


def eliminar_autor(sesion: Session, autor_id: int):
    """
    QUE HACE:
        Elimina un autor de la base de datos.
    QUE RECIBE:
        - sesion: conexion activa.
        - autor_id: ID del autor a eliminar.
    QUE DEVUELVE:
        Mensaje de confirmacion.
    REGLAS QUE APLICA:
        - Regla 7: Si no existe -> error 404.
    """
    autor = obtener_autor_por_id(sesion, autor_id)
    sesion.delete(autor)
    sesion.commit()
    return {"mensaje": "Autor eliminado correctamente"}
