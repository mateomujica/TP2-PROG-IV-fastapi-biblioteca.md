from typing import Optional

from sqlmodel import Session, func, select

from models.libro import Libro
from models.prestamo import Prestamo


def obtener_por_id(sesion: Session, prestamo_id: int) -> Optional[Prestamo]:
    return sesion.get(Prestamo, prestamo_id)


def contar_activos(sesion: Session, socio_id: int) -> int:
    cantidad = sesion.exec(
        select(func.count())
        .select_from(Prestamo)
        .where(
            Prestamo.socio_id == socio_id,
            Prestamo.fecha_devolucion.is_(None),
        )
    ).one()
    return int(cantidad)


def listar_de_socio(
    sesion: Session,
    socio_id: int,
    solo_activos: bool = False,
) -> list[Prestamo]:
    statement = select(Prestamo).where(Prestamo.socio_id == socio_id)
    if solo_activos:
        statement = statement.where(Prestamo.fecha_devolucion.is_(None))
    return list(sesion.exec(statement).all())


def guardar_con_libro(
    sesion: Session,
    prestamo: Prestamo,
    libro: Libro,
) -> Prestamo:
    sesion.add(libro)
    sesion.add(prestamo)
    sesion.commit()
    sesion.refresh(prestamo)
    return prestamo
