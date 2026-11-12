
# Define las rutas HTTP (endpoints) para pedir un prestamo
# y para registrar la devolucion de un libro.


from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from database import obtener_sesion
from models.prestamo import PrestamoCrear, PrestamoDevolucion, PrestamoRespuesta
from services import prestamo_service

router = APIRouter(prefix="/prestamos", tags=["Prestamos"])


@router.post("", response_model=PrestamoRespuesta, status_code=status.HTTP_201_CREATED)
def crear_prestamo(datos: PrestamoCrear, sesion: Session = Depends(obtener_sesion)):
    """
    QUE HACE: Registra un nuevo prestamo aplicando todas las reglas de negocio.
    QUE RECIBE: JSON con socio_id, libro_id y opcionalmente fecha_prestamo.
    QUE LLAMA: prestamo_service.registrar_prestamo.
    QUE DEVUELVE: El prestamo registrado (codigo 201 Created).
    """
    return prestamo_service.registrar_prestamo(sesion, datos)


@router.post("/{id}/devolucion", response_model=PrestamoRespuesta)
def devolver_prestamo(
    id: int,
    datos: Optional[PrestamoDevolucion] = None,
    sesion: Session = Depends(obtener_sesion)
):
    """
    QUE HACE: Registra la devolucion de un libro prestado, reponiendo stock
              y calculando multa si hubo retraso.
    QUE RECIBE: ID del prestamo en la URL y opcionalmente JSON con fecha_devolucion.
    QUE LLAMA: prestamo_service.registrar_devolucion.
    QUE DEVUELVE: El prestamo actualizado con fecha de devolucion y multa.
    """
    return prestamo_service.registrar_devolucion(sesion, prestamo_id=id, datos=datos)
