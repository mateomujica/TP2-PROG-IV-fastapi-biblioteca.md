from typing import Optional

from sqlmodel import Session, select

from models.autor import Autor


def crear(sesion: Session, autor: Autor) -> Autor:
    sesion.add(autor)
    sesion.commit()
    sesion.refresh(autor)
    return autor


def listar(sesion: Session) -> list[Autor]:
    return list(sesion.exec(select(Autor)).all())


def obtener_por_id(sesion: Session, autor_id: int) -> Optional[Autor]:
    return sesion.get(Autor, autor_id)


def actualizar(sesion: Session, autor: Autor, cambios: dict) -> Autor:
    for campo, valor in cambios.items():
        setattr(autor, campo, valor)
    sesion.add(autor)
    sesion.commit()
    sesion.refresh(autor)
    return autor


def eliminar(sesion: Session, autor: Autor) -> None:
    sesion.delete(autor)
    sesion.commit()
