from datetime import date, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session

from models.prestamo import (
    Prestamo,
    PrestamoCrear,
    PrestamoDevolucion,
)
from repositories import libros as libro_repository
from repositories import prestamos as prestamo_repository
from repositories import socios as socio_repository

PLAZO_DIAS = 14
MULTA_POR_DIA = 100
MAX_PRESTAMOS_ACTIVOS = 3


def registrar_prestamo(sesion: Session, datos: PrestamoCrear) -> Prestamo:
    socio = socio_repository.obtener_por_id(sesion, datos.socio_id)
    if socio is None:
        raise HTTPException(status_code=404, detail="Socio no encontrado")

    libro = libro_repository.obtener_por_id(sesion, datos.libro_id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    if not socio.activo:
        raise HTTPException(
            status_code=403,
            detail="Un socio inactivo no puede pedir préstamos",
        )

    if prestamo_repository.contar_activos(sesion, datos.socio_id) >= MAX_PRESTAMOS_ACTIVOS:
        raise HTTPException(
            status_code=409,
            detail="El socio no puede tener más de 3 préstamos activos",
        )

    if libro.stock <= 0:
        raise HTTPException(
            status_code=409,
            detail="No se presta un libro sin stock disponible",
        )

    fecha_prestamo = datos.fecha_prestamo or date.today()
    prestamo = Prestamo(
        socio_id=datos.socio_id,
        libro_id=datos.libro_id,
        fecha_prestamo=fecha_prestamo,
        fecha_vencimiento=fecha_prestamo + timedelta(days=PLAZO_DIAS),
        fecha_devolucion=None,
        multa=0.0,
    )
    libro.stock -= 1

    return prestamo_repository.guardar_con_libro(sesion, prestamo, libro)


def registrar_devolucion(
    sesion: Session,
    prestamo_id: int,
    datos: Optional[PrestamoDevolucion] = None,
) -> Prestamo:
    prestamo = prestamo_repository.obtener_por_id(sesion, prestamo_id)
    if prestamo is None:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    if prestamo.fecha_devolucion is not None:
        raise HTTPException(
            status_code=409,
            detail="No se puede devolver un préstamo ya devuelto",
        )

    libro = libro_repository.obtener_por_id(sesion, prestamo.libro_id)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    fecha_devolucion = (
        datos.fecha_devolucion
        if datos is not None and datos.fecha_devolucion is not None
        else date.today()
    )
    dias_atraso = max(
        0,
        (fecha_devolucion - prestamo.fecha_vencimiento).days,
    )

    prestamo.fecha_devolucion = fecha_devolucion
    prestamo.multa = float(MULTA_POR_DIA * dias_atraso)
    libro.stock += 1

    return prestamo_repository.guardar_con_libro(sesion, prestamo, libro)


def listar_prestamos_de_socio(
    sesion: Session,
    socio_id: int,
    activos: Optional[bool] = None,
):
    socio = socio_repository.obtener_por_id(sesion, socio_id)
    if socio is None:
        raise HTTPException(status_code=404, detail="Socio no encontrado")

    return prestamo_repository.listar_de_socio(
        sesion,
        socio_id,
        solo_activos=activos is True,
    )