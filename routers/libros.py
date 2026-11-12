
# Define las rutas HTTP (endpoints) para manejar los Libros.
# Incluye el CRUD, el filtro por disponibles y asociar autores a un libro.


from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from database import obtener_sesion
from models.libro import LibroCrear, LibroActualizar, LibroRespuesta
from services import libro_service

router = APIRouter(prefix="/libros", tags=["Libros"])


@router.post("", response_model=LibroRespuesta, status_code=status.HTTP_201_CREATED)
def crear_libro(datos: LibroCrear, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Crea un nuevo libro.
    QUE RECIBE: JSON con titulo, isbn, stock y anio.
    QUE LLAMA: libro_service.crear_libro.
    QUE DEVUELVE: El libro creado (codigo 201 Created).
    """
    return libro_service.crear_libro(sesion, datos)


@router.get("", response_model=List[LibroRespuesta])
def listar_libros(disponibles: Optional[bool] = None, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Devuelve la lista de libros con sus autores.
              Si se consulta /libros?disponibles=true solo devuelve con stock > 0.
    QUE RECIBE: Parametro opcional 'disponibles' en la URL.
    QUE LLAMA: libro_service.listar_libros.
    QUE DEVUELVE: Lista de libros con sus autores.
    """
    return libro_service.listar_libros(sesion, disponibles)


@router.get("/{id}", response_model=LibroRespuesta)
def obtener_libro(id: int, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Busca un libro por su ID.
    QUE RECIBE: ID del libro en la URL.
    QUE LLAMA: libro_service.obtener_libro_por_id.
    QUE DEVUELVE: El libro encontrado con sus autores (o 404 si no existe).
    """
    return libro_service.obtener_libro_por_id(sesion, id)


@router.put("/{id}", response_model=LibroRespuesta)
def actualizar_libro(id: int, datos: LibroActualizar, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Modifica los datos de un libro existente.
    QUE RECIBE: ID en la URL y los campos a cambiar en JSON.
    QUE LLAMA: libro_service.actualizar_libro.
    QUE DEVUELVE: El libro modificado.
    """
    return libro_service.actualizar_libro(sesion, id, datos)


@router.delete("/{id}")
def eliminar_libro(id: int, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Borra un libro de la base de datos.
    QUE RECIBE: ID en la URL.
    QUE LLAMA: libro_service.eliminar_libro.
    QUE DEVUELVE: Mensaje de confirmacion.
    """
    return libro_service.eliminar_libro(sesion, id)


@router.post("/{id}/autores/{autor_id}", response_model=LibroRespuesta)
def asociar_autor(id: int, autor_id: int, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Asocia un autor existente a un libro existente (relacion Muchos a Muchos).
    QUE RECIBE: El ID del libro y el ID del autor en la URL.
    QUE LLAMA: libro_service.asociar_autor_a_libro.
    QUE DEVUELVE: El libro actualizado con la lista de sus autores.
    """
    return libro_service.asociar_autor_a_libro(sesion, libro_id=id, autor_id=autor_id)
