
#  Este archivo se encarga de configurar la conexion con la base de datos.
#  Usa SQLite (un archivo local llamado biblioteca.db) y SQLModel.


from sqlmodel import SQLModel, create_engine, Session

# Nombre del archivo donde se guardaran todos los datos de la biblioteca
NOMBRE_BASE_DATOS = "biblioteca.db"
URL_CONEXION = f"sqlite:///{NOMBRE_BASE_DATOS}"

# Creamos el motor de conexion (engine).
# El parametro connect_args={"check_same_thread": False} es necesario en SQLite
# para que FastAPI pueda atender varias peticiones al mismo tiempo.
engine = create_engine(URL_CONEXION, connect_args={"check_same_thread": False})


def crear_tablas():
    """
    QUE HACE:
        Crea todas las tablas en la base de datos si todavia no existen.
    QUE RECIBE:
        Nada.
    QUE LLAMA:
        SQLModel.metadata.create_all(engine)
    QUE DEVUELVE:
        Nada.
    """
    SQLModel.metadata.create_all(engine)


def obtener_sesion():
    """
    QUE HACE:
        Abre una sesion con la base de datos para que un endpoint pueda
        hacer consultas, guardar o borrar cosas, y cuando termina la cierra sola.
    QUE RECIBE:
        Nada.
    QUE DEVUELVE:
        Entrega (yield) una sesion activa de SQLModel.
    COMO SE USA:
        Se usa como dependencia en las rutas de FastAPI con Depends(obtener_sesion).
    """
    with Session(engine) as sesion:
        yield sesion
