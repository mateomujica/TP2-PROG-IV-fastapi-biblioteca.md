from typing import Optional

from sqlmodel import Session, select

from models.prestamo import Prestamo
from models.socio import Socio


def crear(sesion: Session, socio: Socio) -> Socio:
    sesion.add(socio)
    sesion.commit()
    sesion.refresh(socio)
    return socio


def listar(sesion: Session) -> list[Socio]:
    return list(sesion.exec(select(Socio)).all())


def obtener_por_id(sesion: Session, socio_id: int) -> Optional[Socio]:
    return sesion.get(Socio, socio_id)


def obtener_por_email(
    sesion: Session,
    email: str,
    excluir_id: Optional[int] = None,
) -> Optional[Socio]:
    statement = select(Socio).where(Socio.email == email)
    if excluir_id is not None:
        statement = statement.where(Socio.id != excluir_id)
    return sesion.exec(statement).first()


def actualizar(sesion: Session, socio: Socio, cambios: dict) -> Socio:
    for campo, valor in cambios.items():
        setattr(socio, campo, valor)
    sesion.add(socio)
    sesion.commit()
    sesion.refresh(socio)
    return socio


def eliminar(sesion: Session, socio: Socio) -> None:
    prestamos = sesion.exec(
        select(Prestamo).where(Prestamo.socio_id == socio.id)
    ).all()
    for prestamo in prestamos:
        sesion.delete(prestamo)
    sesion.delete(socio)
    sesion.commit()
