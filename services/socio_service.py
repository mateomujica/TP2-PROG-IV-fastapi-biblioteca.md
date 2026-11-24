from fastapi import HTTPException
from sqlmodel import Session

from models.socio import Socio, SocioActualizar, SocioCrear
from repositories import socios as socio_repository


def crear_socio(sesion: Session, datos: SocioCrear) -> Socio:
    existente = socio_repository.obtener_por_email(sesion, datos.email)
    if existente is not None:
        raise HTTPException(status_code=409, detail="Ya existe un socio con ese email")

    socio = Socio.model_validate(datos)
    return socio_repository.crear(sesion, socio)


def listar_socios(sesion: Session):
    return socio_repository.listar(sesion)


def obtener_socio_por_id(sesion: Session, socio_id: int) -> Socio:
    socio = socio_repository.obtener_por_id(sesion, socio_id)
    if socio is None:
        raise HTTPException(status_code=404, detail="Socio no encontrado")
    return socio


def actualizar_socio(sesion: Session, socio_id: int, datos: SocioActualizar) -> Socio:
    socio = obtener_socio_por_id(sesion, socio_id)
    cambios = datos.model_dump(exclude_unset=True)

    if "email" in cambios:
        existente = socio_repository.obtener_por_email(
            sesion,
            cambios["email"],
            excluir_id=socio_id,
        )
        if existente is not None:
            raise HTTPException(status_code=409, detail="Ya existe un socio con ese email")

    return socio_repository.actualizar(sesion, socio, cambios)


def eliminar_socio(sesion: Session, socio_id: int):
    socio = obtener_socio_por_id(sesion, socio_id)
    socio_repository.eliminar(sesion, socio)
    return {"mensaje": "Socio eliminado"}