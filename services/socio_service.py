
# Maneja la creacion, consulta, modificacion y eliminacion de socios,
# asegurando que los correos no se repitan (Regla 8).
from typing import List
from fastapi import HTTPException, status
from sqlmodel import Session, select
from models.socio import Socio, SocioCrear, SocioActualizar
def crear_socio(sesion: Session, datos: SocioCrear) -> Socio:
    """
    QUE HACE:
        Registra un nuevo socio validando que no se repita el email.
    QUE RECIBE:
        - sesion: conexion activa a la base de datos.
        - datos: nombre, email y si esta activo.
    QUE DEVUELVE:
        El socio creado.
    """
    # Buscamos si ya existe alguien con ese email
    consulta = select(Socio).where(Socio.email == datos.email)
    existente = sesion.exec(consulta).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un socio con ese email"
        )

    nuevo_socio = Socio(
        nombre=datos.nombre,
        email=datos.email,
        activo=datos.activo
    )

    sesion.add(nuevo_socio)
    sesion.commit()
    sesion.refresh(nuevo_socio)
    return nuevo_socio


def listar_socios(sesion: Session) -> List[Socio]:
    """
    QUE HACE:
        Devuelve la lista con todos los socios registrados.
    QUE RECIBE:
        - sesion: conexion activa.
    QUE DEVUELVE:
        Lista de socios.
    """
    consulta = select(Socio)
    return sesion.exec(consulta).all()


def obtener_socio_por_id(sesion: Session, socio_id: int) -> Socio:
    """
    QUE HACE:
        Busca un socio por su ID.
    QUE RECIBE:
        - sesion: conexion activa.
        - socio_id: ID del socio a buscar.
    QUE DEVUELVE:
        El socio encontrado.
    """
    socio = sesion.get(Socio, socio_id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Socio no encontrado"
        )
    return socio


def actualizar_socio(sesion: Session, socio_id: int, datos: SocioActualizar) -> Socio:
    """
    QUE HACE:
        Modifica los datos de un socio existente.
    QUE RECIBE:
        - sesion: conexion activa.
        - socio_id: ID del socio a modificar.
        - datos: campos que se quieren cambiar.
    QUE DEVUELVE:
        El socio actualizado.
    """
    socio = obtener_socio_por_id(sesion, socio_id)

    # Si quiere cambiar de email, verificamos que no pertenezca a otra persona
    if datos.email is not None and datos.email != socio.email:
        consulta = select(Socio).where(Socio.email == datos.email)
        existente = sesion.exec(consulta).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un socio con ese email"
            )
        socio.email = datos.email

    if datos.nombre is not None:
        socio.nombre = datos.nombre

    if datos.activo is not None:
        socio.activo = datos.activo

    sesion.add(socio)
    sesion.commit()
    sesion.refresh(socio)
    return socio


def eliminar_socio(sesion: Session, socio_id: int):
    """
    QUE HACE:
        Elimina un socio de la base de datos.
    QUE RECIBE:
        - sesion: conexion activa.
        - socio_id: ID del socio a borrar.
    QUE DEVUELVE:
        Mensaje de confirmacion.
    """
    socio = obtener_socio_por_id(sesion, socio_id)
    sesion.delete(socio)
    sesion.commit()
    return {"mensaje": "Socio eliminado correctamente"}