#Contiene toda la logica y las reglas de negocio de los prestamos
#y devoluciones de la biblioteca.
from datetime import date, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select
from models.prestamo import Prestamo, PrestamoCrear, PrestamoDevolucion
from models.socio import Socio
from models.libro import Libro

def registrar_prestamo(sesion: Session, datos: PrestamoCrear) -> Prestamo:
    """
    QUE HACE:
        Registra un nuevo prestamo aplicando las reglas 1, 2, 3, 4 y 7.
    QUE RECIBE:
        - sesion: la conexion activa con la base de datos.
        - datos: el socio_id, libro_id y opcionalmente la fecha_prestamo.
    QUE LLAMA:
        - Consultas a la base para buscar socio, libro y contar prestamos activos.
    QUE DEVUELVE:
        El prestamo creado y guardado en la base de datos.
    """
    #Buscamos al socio en la base de datos
    socio = sesion.get(Socio, datos.socio_id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Socio no encontrado"
        )

    #Buscamos el libro en la base de datos
    libro = sesion.get(Libro, datos.libro_id)
    if not libro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )

    #Validamos si el socio esta activo 
    if not socio.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Un socio inactivo no puede pedir préstamos"
        )

    # Contamos cuantos prestamos activos tiene el socio 
    # Un prestamo esta activo cuando todavia NO fue devuelto 
    consulta_activos = select(Prestamo).where(
        Prestamo.socio_id == datos.socio_id,
        Prestamo.fecha_devolucion == None
    )
    prestamos_activos = sesion.exec(consulta_activos).all()

    if len(prestamos_activos) >= 3:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El socio no puede tener más de 3 préstamos activos"
        )

    # 5. Validamos si hay stock disponible del libro (Regla 2: stock <= 0 -> 409)
    if libro.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se presta un libro sin stock disponible"
        )

    # Si hay stock, descontamos 1 unidad del libro (Regla 2)
    libro.stock -= 1
    sesion.add(libro)

    # 6. Definimos las fechas del prestamo (Regla 4: 14 dias de plazo)
    fecha_inicio = datos.fecha_prestamo if datos.fecha_prestamo else date.today()
    fecha_limite = fecha_inicio + timedelta(days=14)

    # 7. Creamos el registro del prestamo
    nuevo_prestamo = Prestamo(
        socio_id=datos.socio_id,
        libro_id=datos.libro_id,
        fecha_prestamo=fecha_inicio,
        fecha_vencimiento=fecha_limite,
        fecha_devolucion=None,
        multa=0.0
    )

    sesion.add(nuevo_prestamo)
    sesion.commit()
    sesion.refresh(nuevo_prestamo)

    return nuevo_prestamo


def registrar_devolucion(sesion: Session, prestamo_id: int, datos: Optional[PrestamoDevolucion] = None) -> Prestamo:
    """
    QUE HACE:
        Registra la devolucion de un prestamo aplicando las reglas 5, 6 y 7.
    QUE RECIBE:
        - sesion: conexion a la base de datos.
        - prestamo_id: el numero de ID del prestamo a devolver.
        - datos: opcional, permite enviar una fecha_devolucion especifica (util para tests).
    QUE DEVUELVE:
        El prestamo actualizado con fecha de devolucion y multa calculada.
    """
    # Buscamos el prestamo por su ID
    prestamo = sesion.get(Prestamo, prestamo_id)
    if not prestamo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )

    # Verificamos que no haya sido devuelto antes
    if prestamo.fecha_devolucion is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede devolver un préstamo ya devuelto"
        )

    #Determinamos la fecha de devolucion (hoy o la que mandaron en el cuerpo)
    fecha_entrega = date.today()
    if datos and datos.fecha_devolucion:
        fecha_entrega = datos.fecha_devolucion

    #Calculamos la multa: $100 por dia de atraso si se paso del vencimiento
    multa_calculada = 0.0
    if fecha_entrega > prestamo.fecha_vencimiento:
        dias_de_atraso = (fecha_entrega - prestamo.fecha_vencimiento).days
        multa_calculada = float(dias_de_atraso * 100)

    #Reponemos el stock del libro sumandole 1
    libro = sesion.get(Libro, prestamo.libro_id)
    if libro:
        libro.stock += 1
        sesion.add(libro)

    #Guardamos los cambios en el prestamo
    prestamo.fecha_devolucion = fecha_entrega
    prestamo.multa = multa_calculada

    sesion.add(prestamo)
    sesion.commit()
    sesion.refresh(prestamo)

    return prestamo


def listar_prestamos_de_socio(sesion: Session, socio_id: int, activos: Optional[bool] = None) -> List[Prestamo]:
    """
    QUE HACE:
        Obtiene los prestamos de un socio. Si activos=True, solo devuelve los no devueltos.
    QUE RECIBE:
        - sesion: conexion a la base de datos.
        - socio_id: ID del socio.
        - activos: booleano opcional. Si es True, filtra los que no tienen fecha de devolucion.
    QUE DEVUELVE:
        Lista de prestamos encontrados.
    """
    #Validamos que el socio exista
    socio = sesion.get(Socio, socio_id)
    if not socio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Socio no encontrado"
        )

    #Armamos la consulta
    consulta = select(Prestamo).where(Prestamo.socio_id == socio_id)

    #Si pidieron solo los activos, filtramos donde fecha_devolucion sea None
    if activos is True:
        consulta = consulta.where(Prestamo.fecha_devolucion == None)

    return sesion.exec(consulta).all()
