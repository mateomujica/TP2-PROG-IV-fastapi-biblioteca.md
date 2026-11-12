#Contiene las funciones para crear, consultar, modificar, eliminar
#y asociar autores a los libros, cuidando las reglas de negocio.
from typing import List, Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select
from models.libro import Libro, LibroCrear, LibroActualizar, LibroAutor
from models.autor import Autor
def crear_libro(sesion: Session, datos: LibroCrear) -> Libro:
    """
    QUE HACE:
        Crea un nuevo libro en la base de datos validando que el ISBN no se repita.
    QUE RECIBE:
        - sesion: conexion activa a la base de datos.
        - datos: titulo, isbn, stock y anio.
    QUE DEVUELVE:
        El libro recien creado.
    """
    # Verificamos si ya existe otro libro con el mismo ISBN
    consulta = select(Libro).where(Libro.isbn == datos.isbn)
    existente = sesion.exec(consulta).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un libro con ese ISBN"
        )

    nuevo_libro = Libro(
        titulo=datos.titulo,
        isbn=datos.isbn,
        stock=datos.stock,
        anio=datos.anio
    )

    sesion.add(nuevo_libro)
    sesion.commit()
    sesion.refresh(nuevo_libro)
    return nuevo_libro


def listar_libros(sesion: Session, disponibles: Optional[bool] = None) -> List[Libro]:
    """
    QUE HACE:
        Devuelve la lista de libros. Si disponibles=True, solo los que tienen stock > 0.
    QUE RECIBE:
        - sesion: conexion activa a la base de datos.
        - disponibles: booleano opcional (?disponibles=true en la URL).
    QUE DEVUELVE:
        Lista de libros con sus autores incluidos.
    """
    consulta = select(Libro)

    # Si nos piden solo disponibles, filtramos stock mayor a 0
    if disponibles is True:
        consulta = consulta.where(Libro.stock > 0)

    libros = sesion.exec(consulta).all()
    return libros


def obtener_libro_por_id(sesion: Session, libro_id: int) -> Libro:
    """
    QUE HACE:
        Busca un libro por su ID.
    QUE RECIBE:
        - sesion: conexion activa.
        - libro_id: ID del libro a buscar.
    QUE DEVUELVE:
        El libro encontrado.
    """
    libro = sesion.get(Libro, libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )
    return libro


def actualizar_libro(sesion: Session, libro_id: int, datos: LibroActualizar) -> Libro:
    """
    QUE HACE:
        Modifica los datos de un libro existente.
    QUE RECIBE:
        - sesion: conexion activa.
        - libro_id: ID del libro a editar.
        - datos: campos a actualizar.
    QUE DEVUELVE:
        El libro modificado.
    """
    libro = obtener_libro_por_id(sesion, libro_id)

    # Si quiere cambiar el ISBN, revisamos que ningun otro libro lo tenga
    if datos.isbn is not None and datos.isbn != libro.isbn:
        consulta = select(Libro).where(Libro.isbn == datos.isbn)
        existente = sesion.exec(consulta).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un libro con ese ISBN"
            )
        libro.isbn = datos.isbn

    if datos.titulo is not None:
        libro.titulo = datos.titulo

    if datos.stock is not None:
        if datos.stock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El stock no puede ser negativo"
            )
        libro.stock = datos.stock

    if datos.anio is not None:
        libro.anio = datos.anio

    sesion.add(libro)
    sesion.commit()
    sesion.refresh(libro)
    return libro


def eliminar_libro(sesion: Session, libro_id: int):
    """
    QUE HACE:
        Elimina un libro de la base de datos y sus asociaciones con autores.
    QUE RECIBE:
        - sesion: conexion activa.
        - libro_id: ID del libro a borrar.
    QUE DEVUELVE:
        Un mensaje de confirmacion.
    """
    libro = obtener_libro_por_id(sesion, libro_id)

    # Limpiamos los autores asociados para que no queden referencias huerfanas
    libro.autores.clear()
    sesion.add(libro)

    sesion.delete(libro)
    sesion.commit()
    return {"mensaje": "Libro eliminado correctamente"}


def asociar_autor_a_libro(sesion: Session, libro_id: int, autor_id: int) -> Libro:
    """
    QUE HACE:
        Asocia un autor a un libro en la tabla intermedia (relacion N a N).
    QUE RECIBE:
        - sesion: conexion activa.
        - libro_id: ID del libro.
        - autor_id: ID del autor a vincular.
    QUE DEVUELVE:
        El libro con la lista de autores actualizada.
    """
    # 1. Validamos que el libro exista (Regla 7)
    libro = sesion.get(Libro, libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )

    # 2. Validamos que el autor exista (Regla 7)
    autor = sesion.get(Autor, autor_id)
    if not autor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado"
        )

    # 3. Verificamos si ya estaban asociados para no duplicar
    consulta = select(LibroAutor).where(
        LibroAutor.libro_id == libro_id,
        LibroAutor.autor_id == autor_id
    )
    ya_asociado = sesion.exec(consulta).first()

    if not ya_asociado:
        nueva_asociacion = LibroAutor(libro_id=libro_id, autor_id=autor_id)
        sesion.add(nueva_asociacion)
        sesion.commit()

    sesion.refresh(libro)
    return libro
