# Prueba que la configuracion de base de datos funcione directamente.
from database import obtener_sesion, crear_tablas

def test_obtener_sesion_generador():
    """Prueba que el generador de sesion de database.py entregue una sesion valida"""
    crear_tablas()
    generador = obtener_sesion()
    sesion = next(generador)
    assert sesion is not None
    try:
        next(generador)
    except StopIteration:
        pass  # Es lo esperado al cerrarse el generador
