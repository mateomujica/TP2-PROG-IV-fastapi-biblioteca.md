# Configura el entorno de pruebas para pytest.
# Crea una base de datos SQLite limpia en memoria (RAM)
# para que los tests no toquen la base de datos real
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from main import app
from database import obtener_sesion


@pytest.fixture(name="sesion")
def sesion_fixture():
    """
    QUE HACE:
        Crea una base de datos en memoria para cada test y la destruye al terminar.
    """
    # Usamos sqlite:///:memory: y StaticPool para mantener la misma base en memoria viva durante el test
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as sesion:
        yield sesion

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="cliente")
def cliente_fixture(sesion: Session):
    """
    QUE HACE:
        Crea un cliente HTTP de pruebas (TestClient) para hacer peticiones
        a FastAPI simulando llamadas reales como si fueramos un navegador o Postman.
        Reemplaza la conexion a la base de datos real por la base en memoria.
    """
    def obtener_sesion_en_memoria():
        yield sesion

    # Sobreescribimos la dependencia de la base de datos
    app.dependency_overrides[obtener_sesion] = obtener_sesion_en_memoria

    with TestClient(app) as cliente:
        yield cliente

    # Limpiamos la sobreescritura al terminar
    app.dependency_overrides.clear()
