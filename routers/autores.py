# Define las rutas HTTP (endpoints) para manejar los Autores.
# Se encarga del CRUD: crear, listar, ver uno, actualizar y borrar.
from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from database import obtener_sesion
from models.autor import AutorCrear, AutorActualizar, AutorRespuesta
from services import autor_service

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.post("", response_model=AutorRespuesta, status_code=status.HTTP_201_CREATED)
def crear_autor(datos: AutorCrear, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Crea un nuevo autor.
    QUE RECIBE: JSON con nombre y nacionalidad.
    QUE LLAMA: autor_service.crear_autor.
    QUE DEVUELVE: El autor creado con su ID (codigo 201 Created).
    """
    return autor_service.crear_autor(sesion, datos)


@router.get("", response_model=List[AutorRespuesta])
def listar_autores(sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Obtiene todos los autores de la biblioteca.
    QUE RECIBE: Nada.
    QUE LLAMA: autor_service.listar_autores.
    QUE DEVUELVE: Una lista con todos los autores.
    """
    return autor_service.listar_autores(sesion)


@router.get("/{id}", response_model=AutorRespuesta)
def obtener_autor(id: int, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Busca un autor por su ID.
    QUE RECIBE: El ID del autor en la URL.
    QUE LLAMA: autor_service.obtener_autor_por_id.
    QUE DEVUELVE: Los datos del autor encontrado (o 404 si no existe).
    """
    return autor_service.obtener_autor_por_id(sesion, id)


@router.put("/{id}", response_model=AutorRespuesta)
def actualizar_autor(id: int, datos: AutorActualizar, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Modifica los datos de un autor.
    QUE RECIBE: El ID en la URL y los campos a actualizar en el JSON.
    QUE LLAMA: autor_service.actualizar_autor.
    QUE DEVUELVE: El autor ya modificado.
    """
    return autor_service.actualizar_autor(sesion, id, datos)


@router.delete("/{id}")
def eliminar_autor(id: int, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Borra un autor de la base de datos.
    QUE RECIBE: El ID en la URL.
    QUE LLAMA: autor_service.eliminar_autor.
    QUE DEVUELVE: Mensaje de confirmacion.
    """
    return autor_service.eliminar_autor(sesion, id)
