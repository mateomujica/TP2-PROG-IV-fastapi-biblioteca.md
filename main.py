# Es el punto de entrada de la aplicacion FastAPI.
# Configura la app, crea las tablas al iniciar e incluye todos los routers.
from contextlib import asynccontextmanager
from fastapi import FastAPI

from database import crear_tablas
from routers import autores, libros, socios, prestamos


# lifespan maneja lo que pasa cuando arranca y cuando termina la aplicacion
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Al arrancar: creamos las tablas en la base de datos si no existen
    crear_tablas()
    yield
    # Al apagarse: no hace falta hacer nada especial

# Creamos la aplicacion de FastAPI
app = FastAPI(
    title="Sistema de Biblioteca",
    description="API REST para gestionar catalogo de libros y prestamos de una biblioteca",
    version="1.0.0",
    lifespan=lifespan
)

# Registramos cada grupo de rutas (routers) en la aplicacion principal
app.include_router(autores.router)
app.include_router(libros.router)
app.include_router(socios.router)
app.include_router(prestamos.router)

@app.get("/")
def inicio():
    """
    QUE HACE: Endpoint simple de bienvenida.
    QUE DEVUELVE: Mensaje con enlace a la documentacion interactiva /docs.
    """
    return {
        "mensaje": "Bienvenido al Sistema de Biblioteca",
        "documentacion": "/docs"
    }