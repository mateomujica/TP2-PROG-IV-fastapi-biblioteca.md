
# Define las rutas HTTP (endpoints) para manejar los Socios
# y consultar el historial o prestamos activos de un socio.


from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from database import obtener_sesion
from models.socio import SocioCrear, SocioActualizar, SocioRespuesta
from models.prestamo import PrestamoRespuesta
from services import socio_service, prestamo_service

router = APIRouter(prefix="/socios", tags=["Socios"])


@router.post("", response_model=SocioRespuesta, status_code=status.HTTP_201_CREATED)
def crear_socio(datos: SocioCrear, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Registra un nuevo socio.
    QUE RECIBE: JSON con nombre, email y si esta activo.
    QUE LLAMA: socio_service.crear_socio.
    QUE DEVUELVE: El socio creado (codigo 201 Created).
    """
    return socio_service.crear_socio(sesion, datos)


@router.get("", response_model=List[SocioRespuesta])
def listar_socios(sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Devuelve la lista de todos los socios.
    QUE RECIBE: Nada.
    QUE LLAMA: socio_service.listar_socios.
    QUE DEVUELVE: Lista de socios.
    """
    return socio_service.listar_socios(sesion)


@router.get("/{id}", response_model=SocioRespuesta)
def obtener_socio(id: int, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Busca un socio por su ID.
    QUE RECIBE: ID del socio en la URL.
    QUE LLAMA: socio_service.obtener_socio_por_id.
    QUE DEVUELVE: El socio encontrado (o 404 si no existe).
    """
    return socio_service.obtener_socio_por_id(sesion, id)


@router.put("/{id}", response_model=SocioRespuesta)
def actualizar_socio(id: int, datos: SocioActualizar, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Modifica los datos de un socio.
    QUE RECIBE: ID en la URL y los campos en JSON.
    QUE LLAMA: socio_service.actualizar_socio.
    QUE DEVUELVE: El socio modificado.
    """
    return socio_service.actualizar_socio(sesion, id, datos)


@router.delete("/{id}")
def eliminar_socio(id: int, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Borra un socio de la base de datos.
    QUE RECIBE: ID en la URL.
    QUE LLAMA: socio_service.eliminar_socio.
    QUE DEVUELVE: Mensaje de confirmacion.
    """
    return socio_service.eliminar_socio(sesion, id)


@router.get("/{id}/prestamos", response_model=List[PrestamoRespuesta])
def prestamos_de_socio(id: int, activos: Optional[bool] = None, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Devuelve los prestamos de un socio.
              Si se consulta /socios/{id}/prestamos?activos=true solo devuelve los activos.
    QUE RECIBE: ID del socio en la URL y opcionalmente el filtro 'activos' como parametro query.
    QUE LLAMA: prestamo_service.listar_prestamos_de_socio.
    QUE DEVUELVE: Lista de prestamos del socio.
    """
    return prestamo_service.listar_prestamos_de_socio(sesion, socio_id=id, activos=activos)
